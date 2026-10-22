"""Freeze verified detections, change cable, and send one explicit manual MOVE."""
import hashlib
import json
import math
import os
import threading
import time
import uuid
from copy import deepcopy
from dataclasses import asdict, dataclass
from datetime import datetime, timezone

from robot.controller import ControlError
from vision.target import Target
from .target_manager import eligibility, in_workspace


@dataclass
class SavedTarget:
    record_id: str
    target: Target
    session: str
    speed: float
    saved_at: str
    status: str = 'SAVED'
    message: str = ''


class SnapshotMove:
    def __init__(self, robot, config, calibration_id, storage, calibration_valid=True, clock=time.monotonic):
        self.robot, self.config, self.calibration_id = robot, config, calibration_id
        self.calibration_valid, self.clock = calibration_valid, clock
        self.storage = storage
        self.lock = threading.RLock()
        self.version = 1
        self.session = uuid.uuid4().hex
        self.vision_ready = False
        self.frame_time = None
        self.items, self.targets, self.saved, self.completed = [], [], [], []
        self.batch_id = None
        self.batch_fingerprint = None
        self.active_id = None
        self.fault = False
        self.message = 'Cắm dây camera, CONNECT CAMERA. Có detection và tọa độ là lưu được ngay.'
        self.hold_intent = threading.Event()
        self.shutdown = threading.Event()
        self.thread = None
        self._restore()

    @property
    def cfg(self):
        return self.config['tracking']

    def fingerprint(self):
        content = dict(tracking=self.cfg, workspace=self.config['workspace'],
                       robot_pose=self.config.get('robot_pose', {}), calibration=self.calibration_id)
        return hashlib.sha256(json.dumps(content, sort_keys=True, allow_nan=False).encode()).hexdigest()

    def _dump(self, record):
        return asdict(record)

    def _parse(self, value):
        value = deepcopy(value)
        target = value.pop('target')
        target['xyz'], target['orientation'] = tuple(target['xyz']), tuple(target['orientation'])
        record = SavedTarget(target=Target(**target), **value)
        numbers = record.target.xyz + record.target.orientation + (record.speed, record.target.confidence)
        if (len(record.target.xyz) != 3 or len(record.target.orientation) != 3
                or not all(math.isfinite(v) for v in numbers) or not self.config['speed']['movl']['min'] <= record.speed <= self.config['speed']['movl']['max']
                or any(abs(v) > 180 for v in record.target.orientation)
                or record.status not in ('SAVED', 'SENDING', 'COMPLETE', 'UNCERTAIN')):
            raise ValueError('Snapshot không hợp lệ')
        return record

    def _restore(self):
        if not self.storage.exists():
            return
        try:
            content = json.loads(self.storage.read_text(encoding='utf-8'))
            if content['schema'] != 1 or content['mode'] != ('MOCK' if self.robot.mock else 'REAL'):
                raise ValueError('Sai định dạng hoặc chế độ snapshot')
            self.saved = [self._parse(v) for v in content['saved']]
            self.completed = [self._parse(v) for v in content['completed']]
            self.batch_id, self.batch_fingerprint = content['batch_id'], content['fingerprint']
            self.version = max(1, int(content['config_version']))
            self.fault = bool(content.get('fault'))
            for record in self.saved:
                if record.status == 'SENDING':
                    record.status, record.message = 'UNCERTAIN', 'Phiên trước kết thúc khi đang MOVE; không gửi lại.'
                    self.fault = True
            self.message = 'Đã nạp tọa độ lưu trên đĩa. Chỉ MOVE khi bấm GỬI TỌA ĐỘ ĐÃ LƯU.'
            if self.fault:
                self.message = 'Có MOVE chưa xác minh. Kết nối robot và xác nhận robot đã dừng trước khi tiếp tục.'
        except Exception as exc:
            self.saved, self.completed = [], []
            self.fault = True
            self.message = f'Không đọc được snapshot: {exc}'

    def _persist(self):
        payload = dict(schema=1, mode='MOCK' if self.robot.mock else 'REAL', batch_id=self.batch_id,
                       fingerprint=self.batch_fingerprint, config_version=self.version, fault=self.fault,
                       saved=[self._dump(v) for v in self.saved], completed=[self._dump(v) for v in self.completed])
        self.storage.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.storage.with_suffix('.tmp')
        try:
            with temporary.open('w', encoding='utf-8') as stream:
                json.dump(payload, stream, ensure_ascii=False, indent=2, allow_nan=False)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self.storage)
        except (OSError, ValueError) as exc:
            raise ControlError('STORAGE_ERROR', f'Không lưu được tọa độ: {exc}', 503) from exc

    def publish(self, items, frame_id, stamp, version, ready=True):
        with self.lock:
            if version != self.version:
                return
            self.vision_ready, self.frame_time = ready, stamp
            self.items = items
            self.targets = []
            if ready and self.calibration_valid:
                for item in items:
                    xyz = tuple(item.get('xyz', ()))
                    bbox = tuple(item.get('bbox', ()))
                    confidence = item.get('confidence', 0)
                    valid = (not item.get('error') and len(xyz) == 3 and len(bbox) == 4
                             and all(math.isfinite(v) for v in xyz + bbox + (confidence,))
                             and bbox[0] < bbox[2] and bbox[1] < bbox[3]
                             and confidence >= self.cfg['confidence'])
                    item['reason'] = 'Có tọa độ, lưu được ngay' if valid else item.get('error', 'Detection chưa có tọa độ hợp lệ')
                    if valid:
                        self.targets.append(Target(item['id'], item['instance'], item['name'],
                            tuple(round(v, 3) for v in xyz), tuple(round(self.cfg[a], 3) for a in ('rx', 'ry', 'rz')),
                            confidence, stamp, frame_id, self.calibration_id, version))

    def vision_failed(self, message):
        with self.lock:
            self.vision_ready = False
            self.items, self.targets = [], []
            if not self.saved and not self.fault:
                self.message = message
            # Expected when changing the single cable: stored snapshots survive.

    def _busy(self):
        if self.active_id or self.robot.active or self.robot.move_pending.is_set():
            raise ControlError('MOTION_ACTIVE', 'Đang MOVE; chờ xác minh hoàn thành trước.')

    def _distance(self, target, session):
        own = {v.target.instance: v.target for v in self.completed if v.session == session}
        last = self.completed[-1].target if self.completed else None
        return eligibility(target, own, last, self.cfg['minimum_move_distance_mm'],
                           target.timestamp, 0,
                           self.config['workspace'])

    def capture(self):
        with self.lock:
            self._busy()
            if not self.calibration_valid or not self.vision_ready:
                raise ControlError('CAMERA_NOT_READY', 'Camera/calibration chưa sẵn sàng.')
            targets = sorted(self.targets, key=lambda t: t.object_id)
            if not targets:
                raise ControlError('NO_DETECTION', 'YOLO chưa phát hiện vật có tọa độ hợp lệ để lưu.')
            previous = self.saved, self.batch_id, self.batch_fingerprint
            saved_at = datetime.now(timezone.utc).isoformat()
            self.saved = [SavedTarget(uuid.uuid4().hex, t, self.session, self.cfg['movl_speed'], saved_at) for t in targets]
            self.batch_id, self.batch_fingerprint = uuid.uuid4().hex, self.fingerprint()
            try:
                self._persist()
            except ControlError:
                self.saved, self.batch_id, self.batch_fingerprint = previous
                raise
            self.message = f'Đã lưu {len(self.saved)} target. Ngắt camera, đổi dây sang robot rồi CONNECT ROBOT.'
            if self.fault:
                self.message += ' Tọa độ đã lưu; cần xác nhận lỗi MOVE trước đó trước khi GỬI.'
            self.robot.log('SNAPSHOT', self.message)
            return self.snapshot()

    def _saved_eligibility(self, record):
        if record.status != 'SAVED':
            return False, record.message or record.status, None, None
        if self.fault:
            return False, 'Có MOVE chưa xác minh; không gửi tiếp.', None, None
        if self.active_id:
            return False, 'Đang MOVE', None, None
        if self.batch_fingerprint != self.fingerprint() or record.target.calibration_id != self.calibration_id:
            return False, 'Cấu hình/calibration đã đổi; cần chụp và lưu lại.', None, None
        return self._distance(record.target, record.session)

    def _next(self):
        return min((v for v in self.saved if self._saved_eligibility(v)[0]),
                   key=lambda v: v.target.object_id, default=None)

    def _guard(self, record, pose):
        if self.hold_intent.is_set():
            raise ControlError('HOLD_PENDING', 'Đã yêu cầu HOLD')
        if self.batch_fingerprint != self.fingerprint() or not self.calibration_valid:
            raise ControlError('SNAPSHOT_CHANGED', 'Snapshot/calibration không còn hợp lệ.')
        if not self._distance(record.target, record.session)[0]:
            raise ControlError('DISTANCE_BLOCKED', 'Target không đạt điều kiện khoảng cách/workspace.')
        if not in_workspace(tuple(float(v) for v in pose.fields[:3]), self.config['workspace']):
            raise ControlError('PATH_BLOCKED', 'Vị trí hiện tại ngoài workspace cấu hình.')
        for key, field in [('expected_tool', 7), ('expected_posture', 6)]:
            expected = self.config.get('robot_pose', {}).get(key)
            if expected is not None and int(pose.fields[field]) != expected:
                raise ControlError('TOOL_CHANGED', 'Tool/posture khác cấu hình.')
        # This is an explicitly saved manual target; camera is not required at MOVE.

    def send(self, batch_id, record_id):
        with self.lock:
            self.tick()
            self._busy()
            if batch_id != self.batch_id:
                raise ControlError('STALE_REQUEST', 'Bộ tọa độ đã đổi; tải lại giao diện.')
            record = self._next()
            if record is None:
                raise ControlError('NO_SAVED_TARGET', 'Không có tọa độ đã lưu hợp lệ để gửi.')
            if record.record_id != record_id:
                raise ControlError('STALE_REQUEST', 'ID được chọn đã đổi; tải lại trạng thái.')
            if not self.robot.is_connected():
                raise ControlError('DISCONNECTED', 'Đổi dây và CONNECT ROBOT trước khi gửi.')
            record.status, record.message = 'SENDING', 'Đang kiểm tra và gửi MOVE'
            try:
                self._persist()  # Durable intent before any possible wire transmission.
            except ControlError:
                record.status, record.message = 'SAVED', 'Chưa gửi MOVE vì không ghi được dữ liệu.'
                raise
            wire_ready = False
            def guard(pose):
                nonlocal wire_ready
                self._guard(record, pose)
                wire_ready = True
            try:
                self.robot.move_cartesian('MOVL', record.speed,
                    list(record.target.xyz + record.target.orientation), send_guard=guard)
            except Exception as exc:
                if wire_ready:
                    record.status = 'UNCERTAIN'
                    self.fault = True
                else:
                    record.status = 'SAVED'
                record.message = str(exc)
                self.message = str(exc)
                self._persist()
                raise
            self.active_id = record.record_id
            self.message = f'MOVE ID {record.target.object_id} đã được nhận; đang xác minh vị trí.'
            self.robot.log('SNAPSHOT', self.message)
            return self.snapshot()

    def tick(self):
        with self.lock:
            if not self.active_id:
                return
            record = next(v for v in self.saved if v.record_id == self.active_id)
            state = self.robot.snapshot()
            phase = (state['motion'] or {}).get('phase')
            if state['connected'] and phase == 'MOVE COMPLETE':
                record.status, record.message = 'COMPLETE', 'Đã dừng đúng đích qua hai mẫu vị trí.'
                self.completed.append(deepcopy(record))
                self.active_id = None
                self.message = f'ID {record.target.object_id} hoàn thành. Bấm GỬI để chạy ID tiếp theo.'
                self._persist()
            elif not state['connected'] or state['error'] or phase not in ('COMMAND ACCEPTED', 'MOVING / VERIFYING'):
                record.status = 'UNCERTAIN'
                record.message = f'Chuyển động chưa xác minh: {phase or state["error"]}. Không gửi lại.'
                self.active_id = None
                self.fault = True
                self.message = record.message
                self._persist()

    def connect_robot(self, ip, port):
        with self.lock:
            self.tick()
            self._busy()
            if self.robot.is_connected():
                if (self.robot.state['ip'], self.robot.state['port']) == (ip, port):
                    return self.robot.read_status()
                raise ControlError('ALREADY_CONNECTED', 'Ngắt robot trước khi đổi địa chỉ.')
            return self.robot.connect(ip, port)

    def disconnect_robot(self):
        with self.lock:
            self._busy()
            return self.robot.disconnect()

    def acknowledge_fault(self):
        with self.lock:
            self._busy()
            self.robot.read_status()
            state = self.robot.snapshot()
            if not state['connected'] or self.robot.blocked(state['flags']):
                raise ControlError('ROBOT_NOT_READY', 'Robot chưa dừng hoặc còn alarm/HOLD/servo/remote chưa sẵn sàng.')
            self.robot.read_cartesian()
            self.fault = False
            self.hold_intent.clear()
            self.message = 'Đã xác nhận robot dừng. Target UNCERTAIN không được gửi lại; chụp/lưu bộ mới nếu cần.'
            self._persist()

    def hold(self):
        if not self.robot.is_connected():
            raise ControlError('DISCONNECTED', 'Chưa kết nối robot; không gửi HOLD.')
        self.hold_intent.set()
        self.robot.hold_pending.set()
        try:
            return self.robot.hold()
        finally:
            with self.lock:
                self.tick()
                self.fault = True
                self.message = 'Đã yêu cầu HOLD. Kiểm tra robot và xác nhận lại trước khi tiếp tục.'
                self._persist()

    def release_hold(self):
        with self.lock:
            self.tick()
            self._busy()
            result = self.robot.release_hold()
            if not result['flags']['hold'] and not self.robot.hold_pending.is_set():
                self.hold_intent.clear()
            self.fault = True  # Acknowledgement remains a separate explicit operator action.
            self.message = result['message']
            self._persist()
            return result

    def update_config(self, changes):
        with self.lock:
            self._busy()
            self.cfg.update(changes)
            self.version += 1
            self.targets, self.items, self.saved = [], [], []
            self.batch_id = self.batch_fingerprint = None
            self._persist()
            self.message = 'Cấu hình đã đổi; có detection và tọa độ mới thì bấm lưu lại.'

    def snapshot(self):
        with self.lock:
            rows = []
            for item in self.items:
                row = deepcopy(item)
                target = next((t for t in self.targets if t.object_id == item['id']), None)
                result = (target is not None, item.get('reason', 'Chưa có tọa độ hợp lệ'), None, None)
                if not self.vision_ready:
                    result = (False, 'camera disconnected', None, None)
                row.update(eligible=result[0], reason=result[1], distance_last_mm=result[2], distance_same_id_mm=result[3])
                rows.append(row)
            saved_rows = []
            for record in self.saved:
                ok, reason, distance, own = self._saved_eligibility(record)
                saved_rows.append(dict(**self._dump(record), eligible=ok, reason=reason,
                                       distance_last_mm=distance, distance_same_id_mm=own))
            next_record = self._next()
            can_capture = bool(self.vision_ready and self.calibration_valid and self.targets
                               and not self.active_id and not self.robot.active
                               and not self.robot.move_pending.is_set())
            capture_reason = ('Có XYZ, bấm LƯU được ngay. Lỗi robot chỉ chặn GỬI MOVE.' if self.fault else
                              'Có XYZ, bấm LƯU được ngay.') if can_capture else (
                              'Đang MOVE, chờ robot dừng.' if self.active_id or self.robot.active else
                              'Chờ camera/YOLO trả về tọa độ XYZ hợp lệ.')
            return dict(phase='FAULT' if self.fault else 'MOVING' if self.active_id else
                        'COMPLETE' if self.saved and all(v.status == 'COMPLETE' for v in self.saved) else
                        'SAVED' if self.saved else 'CAMERA',
                        message=self.message, tracking=deepcopy(self.cfg), config_version=self.version,
                        live=rows, saved=saved_rows, batch_id=self.batch_id, active_id=self.active_id,
                        can_capture=can_capture, capture_reason=capture_reason,
                        next_record_id=next_record.record_id if next_record else None,
                        next_object_id=next_record.target.object_id if next_record else None,
                        completed_count=len(self.completed), calibration_valid=self.calibration_valid,
                        storage=str(self.storage))

    def start_worker(self):
        if self.thread and self.thread.is_alive():
            return
        def work():
            while not self.shutdown.wait(.1):
                try:
                    self.tick()
                except Exception as exc:
                    with self.lock:
                        self.fault = True
                        self.message = f'Lỗi lưu/xác minh kết quả: {exc}'
        self.thread = threading.Thread(target=work, name='snapshot-completion', daemon=True)
        self.thread.start()

    def close(self):
        self.shutdown.set()
        if self.thread:
            self.thread.join(timeout=2)
