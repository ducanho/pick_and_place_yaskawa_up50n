import threading
import time
from copy import deepcopy
import cv2
import numpy as np
from settings import owned
from .calibration import PixelToRobot
from .detector import Detector
from .camera import MvsCamera
from .tracker import BoardTracker
from .stability import StableTarget


class Vision:
    def __init__(self, cfg, mock):
        self.cfg, self.mock = cfg, mock
        self.lock = threading.RLock()
        self.stop = threading.Event()
        self.thread = None
        self.camera = None
        self.detector = None
        self.calibration = PixelToRobot(owned('calibration/eye_to_hand.npz'))
        # Verify the second, copied intrinsic asset is readable as well.
        with np.load(owned('calibration/camera_intrinsic_2.npz'), allow_pickle=False) as intrinsic:
            self.intrinsic_keys = list(intrinsic.files)
            if not np.allclose(intrinsic['K'],self.calibration.K) or not np.allclose(intrinsic['distortion'].reshape(-1),self.calibration.distortion):
                raise RuntimeError('Intrinsic và Eye-to-Hand không khớp')
        self.connected = False
        self.error = ''
        self.preview = None
        self.frame_id, self.stamp, self.items, self.fps = 0, 0, [], 0
        self.tracker = BoardTracker()
        self._next_target = None

    def connect(self):
        if self.connected:
            return
        if self.thread and self.thread.is_alive():
            raise RuntimeError('Camera worker vẫn đang dừng')
        self.clear_next_pick()
        if not self.mock:
            self.detector = Detector(owned('models/best.pt'), self.cfg['vision'])
            if self.camera:
                self.camera.close()
            self.camera = MvsCamera(self.cfg['vision']['sdk_root'])
            devices = self.camera.enumerate()
            # Match actual GigE IP, never silently select a different camera.
            import ctypes as ct
            import ipaddress
            m = self.camera.module
            matches = []
            for d in devices:
                info = ct.cast(self.camera.devices.pDeviceInfo[d['index']], ct.POINTER(m.MV_CC_DEVICE_INFO)).contents
                if info.nTLayerType == m.MV_GIGE_DEVICE and str(ipaddress.IPv4Address(info.SpecialInfo.stGigEInfo.nCurrentIp)) == self.cfg['camera_ip']:
                    matches.append(d['index'])
            if len(matches) != 1:
                raise RuntimeError('Không tìm thấy đúng một camera GigE tại IP đã cấu hình')
            self.camera.connect(matches[0])
        self.stop.clear()
        self.connected, self.error = True, ''
        self.thread = threading.Thread(target=self._work, daemon=True, name='vision')
        self.thread.start()

    def _work(self):
        last = -1
        started = time.monotonic()
        while not self.stop.wait(.1):
            try:
                with self.lock:
                    settings = deepcopy(self.cfg['settings'])
                if self.mock:
                    frame = np.full((540, 960, 3), 25, dtype=np.uint8)
                    stamp, frame_id = time.monotonic(), self.frame_id+1
                    items = [dict(name='MOCK', confidence=.97, bbox=(150+300*i,200,250+300*i,300),
                                  u=200+300*i, v=250, xyz=(850.+200*i, 100., settings['plane_z_mm'])) for i in range(2)]
                else:
                    frame_id, stamp, frame = self.camera.sample()
                    if frame_id == last:
                        continue
                    items = self.detector.detect(frame, self.calibration, {**settings, 'confidence':self.cfg['vision']['confidence']})
                items = self.tracker.update(items, stamp)
                last = frame_id
                scale = min(1, 960/frame.shape[1])
                image = cv2.resize(frame, (round(frame.shape[1]*scale), round(frame.shape[0]*scale)))
                for item in items:
                    a,b,c,d = [round(v*scale) for v in item['bbox']]
                    cv2.rectangle(image,(a,b),(c,d),(80,220,140),2)
                    xy = item.get('xyz', (0,0))
                    cv2.putText(image,f'ID {item["id"]} {item["confidence"]:.2f} X {xy[0]:.1f} Y {xy[1]:.1f}',
                                (a,max(20,b-10)),cv2.FONT_HERSHEY_SIMPLEX,.5,(80,220,140),1)
                ok, jpeg = cv2.imencode('.jpg', image)
                with self.lock:
                    self.fps = 1/max(time.monotonic()-started,.001)
                    started = time.monotonic()
                    self.frame_id,self.stamp,self.items = frame_id,stamp,items
                    if self._next_target is not None:
                        self._next_target.update(frame_id,stamp,items,time.monotonic())
                    if ok:
                        self.preview = jpeg.tobytes()
            except Exception as exc:
                if self.frame_id == 0 and time.monotonic()-started < 3:
                    continue
                with self.lock:
                    self.connected,self.error,self.items = False,str(exc),[]
                    self._next_target = None
                self.stop.set()

    def prepare_next_pick(self,after_id):
        with self.lock:
            self._next_target=StableTarget(deepcopy(self.cfg['vision']),after_id=after_id)

    def take_next_pick(self,after_id):
        with self.lock:
            target=self._next_target
            self._next_target=None
            if target is not None and target.after_id==after_id:
                return deepcopy(target)
            return None

    def clear_next_pick(self):
        with self.lock:
            self._next_target=None

    def sample(self):
        with self.lock:
            if not self.connected or time.monotonic()-self.stamp > self.cfg['vision']['max_frame_age']:
                raise RuntimeError(self.error or 'Camera không có frame mới')
            return self.frame_id, self.stamp, deepcopy(self.items)

    def status(self):
        with self.lock:
            return dict(connected=self.connected and time.monotonic()-self.stamp <= self.cfg['vision']['max_frame_age'],
                        error=self.error, fps=round(self.fps,1), detections=deepcopy(self.items),
                        frame_id=self.frame_id, simulated=self.mock,
                        model_loaded=self.detector is not None, calibration=self.calibration.quality,
                        calibration_warning=self.calibration.quality_message() if self.calibration.quality != 'residual_checks_passed' else '',
                        coordinates_verified=self.calibration.quality == 'residual_checks_passed')

    def close(self):
        self.clear_next_pick()
        self.stop.set()
        if self.thread:
            self.thread.join(timeout=5)
            if self.thread.is_alive():
                raise RuntimeError('Vision worker chưa dừng')
        if self.camera:
            self.camera.close()
        self.connected = False
