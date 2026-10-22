import hashlib
import threading
import time
from copy import deepcopy

import cv2
import numpy as np

from .calibration import PixelToRobot, InputError
from .camera import MvsCamera
from .detector import Detector
from .tracker import BoardTracker


def load_calibration(base):
    path = base / 'calibration/eye_to_hand.npz'
    calibration = PixelToRobot(path)
    with np.load(base / 'calibration/camera_intrinsic_2.npz', allow_pickle=False) as intrinsic:
        if (not np.array_equal(intrinsic['K'], calibration.K)
                or not np.array_equal(intrinsic['distortion'].ravel(), calibration.distortion)
                or (int(intrinsic['image_width']), int(intrinsic['image_height'])) != calibration.size):
            raise InputError('Intrinsic differs from Eye-to-Hand calibration')
    return calibration, hashlib.sha256(path.read_bytes()).hexdigest()


class VisionPipeline:
    def __init__(self, base, auto, calibration):
        self.base, self.auto, self.calibration = base, auto, calibration
        self.mock = auto.robot.mock
        self.lock = threading.RLock()
        self.lifecycle_lock = threading.Lock()
        self.camera = self.detector = self.thread = None
        self.stop = threading.Event()
        self.connected = False
        self.error = ''
        self.preview = None
        self.fps = 0.0
        self.frame_id = 0
        self.tracker = BoardTracker()

    def scan(self):
        with self.lifecycle_lock:
            if self.mock:
                return [dict(index=0, name='MOCK HIKROBOT + synthetic detections')]
            if self.camera is None:
                self.camera = MvsCamera(self.auto.config['vision'].get('sdk_root'))
            return self.camera.enumerate()

    def connect(self, index):
        with self.lifecycle_lock:
            if self.connected or (self.thread and self.thread.is_alive()):
                raise InputError('Disconnect camera before connecting again')
            if self.mock and index != 0:
                raise InputError('Mock camera index must be 0')
            if not self.mock:
                if self.calibration is None:
                    raise InputError('Invalid calibration')
                if self.detector is None:
                    self.detector = Detector(self.base / 'models/best.pt', self.auto.config['vision'])
                if self.camera is None:
                    raise InputError('Scan camera first')
                self.camera.connect(index)
            self.connected, self.error = True, ''
            self.stop.clear()
            self.thread = threading.Thread(target=self._work, daemon=True, name='yolo-inference')
            self.thread.start()
            self.auto.robot.log('VISION', 'Camera connected (MOCK)' if self.mock else 'HIKROBOT connected')

    def _work(self):
        last_frame = -1
        last_processed = time.monotonic()
        while not self.stop.wait(.02):
            try:
                with self.auto.lock:
                    cfg, version = deepcopy(self.auto.cfg), self.auto.version
                if self.mock:
                    if time.monotonic() - last_processed < .095:
                        continue
                    self.frame_id += 1
                    frame_id, stamp = self.frame_id, time.monotonic()
                    frame = np.full((540, 960, 3), 22, np.uint8)
                    items = []
                    for i, x in enumerate((850, 1050, 1250)):
                        u, v = 180 + i * 280, 240
                        items.append(dict(name='MOCK object', confidence=.96, bbox=(u-50, v-40, u+50, v+40),
                                          u=u, v=v, xyz=(float(x), float(120-i*110), cfg['plane_z_mm'])))
                else:
                    frame_id, stamp, frame = self.camera.sample()
                    if frame_id == last_frame:
                        continue
                    self.calibration.check_frame(frame)
                    items = self.detector.detect(frame, self.calibration, cfg)
                last_frame = frame_id
                items = self.tracker.update(items, stamp)
                for item in items:
                    item['orientation'] = [cfg[a] for a in ('rx', 'ry', 'rz')]
                self.auto.publish(items, frame_id, stamp, version)
                now = time.monotonic()
                self.fps = 1 / max(now - last_processed, .001)
                last_processed = now
                self._render(frame, items)
            except Exception as exc:
                self.auto.vision_failed(f'Vision unavailable: {exc}')
                self.error = str(exc)
                # Allow a short startup interval for the first MVS frame.
                if not self.mock and self.camera.connected and not self.camera.error and last_frame == -1:
                    continue
                self.connected = False
                self.stop.set()

    def _render(self, frame, items):
        scale = min(1, self.auto.config['vision']['preview_max_width'] / frame.shape[1])
        preview = cv2.resize(frame, (round(frame.shape[1] * scale), round(frame.shape[0] * scale)))
        for item in items:
            a, b, c, d = [round(v * scale) for v in item['bbox']]
            cv2.rectangle(preview, (a, b), (c, d), (80, 230, 70), 2)
            cv2.putText(preview, f'ID {item["id"]}: {item["name"]} {item["confidence"]:.2f}',
                        (a, max(b-8, 20)), cv2.FONT_HERSHEY_SIMPLEX, .5, (80, 230, 70), 1)
        ok, jpeg = cv2.imencode('.jpg', preview, [cv2.IMWRITE_JPEG_QUALITY, 80])
        if ok:
            with self.lock:
                self.preview = jpeg.tobytes()

    def status(self):
        return dict(connected=self.connected, fps=round(self.fps, 1), error=self.error,
                    mode='MOCK' if self.mock else 'REAL', model_loaded=self.mock or self.detector is not None)

    def disconnect(self):
        with self.lifecycle_lock:
            self.stop.set()
            if self.thread:
                self.thread.join(timeout=5)
                if self.thread.is_alive():
                    raise InputError('Inference still running; wait before disconnecting again')
            if self.camera:
                self.camera.disconnect()
            self.connected = False
            with self.lock:
                self.preview = None
            self.auto.vision_failed('Camera disconnected')

    def close(self):
        self.disconnect()
        if self.camera:
            self.camera.close()
