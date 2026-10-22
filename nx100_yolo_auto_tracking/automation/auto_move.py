"""One serialized automation owner; immutable in-flight target; no MOVE retries."""
import threading
import time
from dataclasses import asdict
from copy import deepcopy

from robot.controller import ControlError
from vision.stability import Stability
from .state_machine import State
from .target_manager import eligibility, in_workspace, select_next_target


class Automation:
    def __init__(self, robot, config, calibration_id, calibration_valid=True, clock=time.monotonic):
        self.robot, self.config, self.clock = robot, config, clock
        self.calibration_id, self.calibration_valid = calibration_id, calibration_valid
        self.lock = threading.RLock()
        self.stability = Stability()
        self.version = 1
        self.state = State.DISCONNECTED
        self.armed = False
        self.stop_requested = threading.Event()
        self.shutdown = threading.Event()
        self.thread = None
        self.vision_ready = False
        self.frame_time = None
        self.items, self.targets = [], []
        self.selected = None
        self.last_completed_robot_target = None
        self.completed_targets_by_id = {}  # Internal instance, not reusable display ID.
        self.completed_sites = []
        self.home_active = False
        self.message = 'Connect robot and camera, then START'
        self.last_decisions = {}

    def transition(self, state, message=''):
        if self.state != state or (message and self.message != message):
            self.robot.log('AUTO', f'{state.value}: {message}')
        self.state = state
        if message:
            self.message = message

    def fault(self, message):
        self.armed = False
        self.targets = []
        self.transition(State.FAULT, message)

    def _vision_check(self):
        if not self.calibration_valid:
            raise ControlError('CALIBRATION_INVALID', 'Calibration is invalid')
        if not self.vision_ready or self.frame_time is None or not 0 <= self.clock() - self.frame_time <= self.cfg['max_frame_age_ms'] / 1000:
            raise ControlError('VISION_NOT_READY', 'Camera / YOLO frame unavailable or stale')

    @property
    def cfg(self):
        return self.config['tracking']

    def _real_check(self, pose=None):
        if self.robot.mock:
            return
        v = self.config.get('robot_pose', {})
        if pose is not None:
            for field, index in [('expected_tool', 7), ('expected_posture', 6)]:
                if v.get(field) is not None and int(pose.fields[index]) != v[field]:
                    raise ControlError('TOOL_POSTURE_CHANGED', 'Tool / posture differs from configured value')

    def start(self):
        with self.lock:
            if self.armed:
                return
            if self.state == State.FAULT:
                raise ControlError('FAULT_LATCHED', 'Restart backend after inspecting the fault; automatic recovery disabled')
            if self.robot.active or self.home_active:
                raise ControlError('MOTION_ACTIVE', 'Wait for current motion')
            self._vision_check()
            self._real_check()
            self.robot.read_status()
            s = self.robot.snapshot()
            reasons = self.robot.blocked(s['flags']) if s['connected'] and s['flags'] else ['Robot disconnected']
            if reasons:
                raise ControlError('START_BLOCKED', '; '.join(reasons))
            self.stop_requested.clear()
            self.stability.reset()
            self.targets = []
            self.armed = True
            self.transition(State.ARMED, 'START: stability begins with new frames')

    def stop(self):
        if self.state in (State.STOPPED, State.FAULT):
            return
        self.stop_requested.set()  # Set before waiting for the automation lock.
        with self.lock:
            if self.state == State.FAULT:
                return
            self.armed = False
            self.targets = []
            self.transition(State.STOP_REQUESTED, 'Finish current motion; no further target MOVE')

    def hold(self):
        self.stop_requested.set()
        # Mark robot priority intent before acquiring automation lock.
        self.robot.hold_pending.set()
        try:
            result = self.robot.hold()
        finally:
            with self.lock:
                self.fault('Operator HOLD; inspect robot before restarting backend')
        return result

    def update_config(self, changes):
        with self.lock:
            self.cfg.update(changes)
            self.version += 1
            self.stability.reset()
            self.targets, self.items = [], []
            self.robot.log('CONFIG', f'Config version {self.version}; unsent targets invalidated')

    def publish(self, items, frame_id, stamp, version, ready=True):
        with self.lock:
            if version != self.version:
                return
            self.vision_ready, self.frame_time = ready, stamp
            self.items = items
            if ready and self.armed:
                self.targets = self.stability.update(items, frame_id, stamp, self.clock(), self.cfg,
                                                     self.version, self.calibration_id)
            else:
                self.stability.reset()
                self.targets = []

    def vision_failed(self, message):
        with self.lock:
            self.vision_ready = False
            self.targets, self.items = [], []
            self.stability.reset()
            if self.armed or self.selected or self.home_active:
                self.fault(message)

    def _assess(self, target):
        return eligibility(target, self.completed_targets_by_id, self.last_completed_robot_target,
                           self.cfg['minimum_move_distance_mm'], self.clock(),
                           self.cfg['max_frame_age_ms'] / 1000, self.config['workspace'], self.completed_sites)

    def _send_guard(self, target, pose):
        if self.stop_requested.is_set() or not self.armed:
            raise ControlError('TARGET_CANCELLED', 'STOP before MOVE send')
        self._vision_check()
        if target.config_version != self.version or target.calibration_id != self.calibration_id or target not in self.targets:
            raise ControlError('TARGET_CANCELLED', 'Target invalidated')
        if not self._assess(target)[0]:
            raise ControlError('TARGET_CANCELLED', 'Target no longer eligible')
        self._real_check(pose)
        if not in_workspace(tuple(float(v) for v in pose.fields[:3]), self.config['workspace']):
            raise ControlError('PATH_BLOCKED', 'Current pose outside validated convex workspace')

    def _home_guard(self, pose):
        self._real_check(pose)
        if not in_workspace(tuple(float(v) for v in pose.fields[:3]), self.config['workspace']) or not in_workspace(self.config['home'][:3], self.config['workspace']):
            raise ControlError('HOME_BLOCKED', 'HOME path endpoints outside workspace')

    def _return_home(self):
        self.home_active = True
        self.transition(State.RETURNING_HOME, 'Operator STOP: returning HOME')
        self.robot.move_cartesian('MOVL', self.cfg['movl_speed'], self.config['home'], send_guard=self._home_guard)

    def tick(self):
        with self.lock:
            if self.state == State.FAULT:
                return
            try:
                s = self.robot.snapshot()
                if self.selected or self.home_active:
                    motion = s['motion'] or {}
                    if not s['connected'] or s['error']:
                        self.fault('Communication lost; no resend and no HOME')
                        return
                    phase = motion.get('phase')
                    if phase == 'MOVE COMPLETE':
                        if self.home_active:
                            self.home_active = False
                            self.stop_requested.clear()
                            self.transition(State.STOPPED, 'HOME confirmed')
                            return
                        t = self.selected
                        self.last_completed_robot_target = t
                        self.completed_targets_by_id[t.instance] = t
                        self.completed_sites.append(t)
                        self.selected = None
                        self.targets = []
                        self.stability.reset()
                        self.transition(State.MOVE_COMPLETE, f'ID {t.object_id} complete; history committed')
                        if self.stop_requested.is_set():
                            self._return_home()
                        else:
                            self.transition(State.WAITING_TARGET, 'Require fresh camera confirmation after completion')
                    elif phase not in ('COMMAND ACCEPTED', 'MOVING / VERIFYING'):
                        self.fault(f'Motion unconfirmed: {phase}; no retry')
                    elif not self.home_active:
                        self.transition(State.STOP_REQUESTED if self.stop_requested.is_set() else
                                        State.MOVING if (s['flags'] or {}).get('running') else State.VERIFYING_POSITION)
                    return
                if self.stop_requested.is_set():
                    self._return_home()
                    return
                if not self.armed:
                    if self.state in (State.DISCONNECTED, State.IDLE):
                        self.transition(State.IDLE if s['connected'] else State.DISCONNECTED)
                    return
                self._vision_check()
                if not s['connected'] or s['error']:
                    raise ControlError('ROBOT_LOST', 'Robot disconnected / error')
                self._decorate()
                target = select_next_target(self.targets, self.completed_targets_by_id,
                        self.last_completed_robot_target, self.cfg['minimum_move_distance_mm'], now=self.clock(),
                        max_age=self.cfg['max_frame_age_ms'] / 1000, workspace=self.config['workspace'],
                        completed_sites=self.completed_sites)
                if target is None:
                    self.transition(State.STABILIZING if self.items else State.WAITING_TARGET)
                    return
                self.transition(State.TARGET_READY, f'ID {target.object_id}: lowest eligible ID')
                self.transition(State.PRECHECK)
                self.robot.move_cartesian('MOVL', self.cfg['movl_speed'], list(target.xyz + target.orientation),
                                           send_guard=lambda pose: self._send_guard(target, pose))
                self.selected = target
                self.transition(State.MOVING, f'MOVE ID {target.object_id} accepted; completion pending')
            except ControlError as exc:
                if exc.code in ('BUSY', 'TARGET_CANCELLED'):
                    return
                self.fault(f'{exc.code}: {exc}')
            except Exception as exc:
                self.fault(f'Unexpected automation error: {exc}')

    def _decorate(self):
        by_id = {t.object_id: t for t in self.targets}
        for item in self.items:
            t = by_id.get(item['id'])
            ok, reason, d, own = self._assess(t) if t else (False, item.get('reason', 'stabilizing'), None, None)
            if not self.vision_ready or self.frame_time is None or self.clock() - self.frame_time > self.cfg['max_frame_age_ms'] / 1000:
                ok, reason = False, 'camera unavailable / stale'
            elif self.selected or self.home_active:
                ok, reason = False, 'robot busy; revalidate after completion'
            if self.state == State.FAULT:
                ok, reason = False, 'automation fault; no MOVE'
            item.update(eligible=ok, reason=reason, distance_last_mm=d, distance_same_id_mm=own)
            if self.last_decisions.get(item['instance']) != reason:
                self.last_decisions[item['instance']] = reason
                self.robot.log('TARGET', f'ID {item["id"]}: {reason}')

    def snapshot(self):
        with self.lock:
            self._decorate()
            return dict(state=self.state.value, armed=self.armed, stop_requested=self.stop_requested.is_set(),
                        message=self.message, config_version=self.version, tracking=deepcopy(self.cfg),
                        selected=asdict(self.selected) if self.selected else None,
                        last_completed=asdict(self.last_completed_robot_target) if self.last_completed_robot_target else None,
                        targets=deepcopy(self.items), eligible_count=sum(bool(i.get('eligible')) for i in self.items),
                        calibration_id=self.calibration_id, calibration_valid=self.calibration_valid)

    def start_worker(self):
        with self.lock:
            if self.thread and self.thread.is_alive():
                return
            def work():
                while not self.shutdown.wait(.05):
                    self.tick()
            self.thread = threading.Thread(target=work, daemon=True, name='automation')
            self.thread.start()

    def close(self):
        self.shutdown.set()
        if self.thread:
            self.thread.join(timeout=self.config['timeout_seconds'] + 1)
