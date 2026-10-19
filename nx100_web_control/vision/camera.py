"""Reuse the calibration project's Hikrobot MVS adapter; explicit camera connect only."""

import base64
import importlib
import sys
import threading
import time
import uuid
from collections import OrderedDict
from pathlib import Path

import cv2
import numpy as np

from .calibration import Calibration, VisionError


class VisionService:
    def __init__(self, config, mock=False):
        self.config, self.mock = config, mock
        self.lock = threading.RLock()
        self.adapter = None
        self.mock_connected = False
        self.frames = OrderedDict()
        self.calibration = None
        self.calibration_error = None
        self.mock_preview = None
        self.reload()

    def reload(self):
        with self.lock:
            self.frames.clear()
            try:
                self.calibration = Calibration(self.config["calibration_file"])
                self.calibration_error = None
            except (OSError, ValueError, KeyError, TypeError) as exc:
                self.calibration = None
                self.calibration_error = str(exc)
            self.mock_preview = None
            return self.status()

    def _calibration(self):
        if self.calibration is None:
            raise VisionError("Chưa đọc được calib: " + str(self.calibration_error))
        return self.calibration

    def _adapter(self):
        if self.adapter is None:
            project = Path(self.config["camera_project"]).resolve()
            if not (project / "calib_mvs.py").is_file():
                raise VisionError("Không tìm thấy calib_mvs.py trong camera_project.")
            # Read-only import of the existing adapter and its local helpers.
            previous = sys.dont_write_bytecode
            sys.dont_write_bytecode = True
            sys.path.insert(0, str(project))
            try:
                self.adapter = importlib.import_module("calib_mvs").MvsCamera()
            finally:
                sys.path.remove(str(project))
                sys.dont_write_bytecode = previous
        return self.adapter

    def status(self):
        with self.lock:
            camera = (
                dict(available=True, connected=self.mock_connected, message="MOCK camera")
                if self.mock
                else self.adapter.status()
                if self.adapter
                else dict(
                    available=None, connected=False, message="Nhấn FIND CAMERA để nạp MVS SDK."
                )
            )
            return dict(
                mode="MOCK" if self.mock else "REAL",
                camera=camera,
                calibration=self.calibration.summary() if self.calibration else None,
                calibration_error=self.calibration_error,
                plane_z_mm=self.config.get("work_plane_z_mm"),
            )

    def enumerate(self):
        with self.lock:
            return (
                [{"index": 0, "name": "MOCK — calibration-size test pattern"}]
                if self.mock
                else self._adapter().enumerate()
            )

    def connect(self, index):
        with self.lock:
            if self.mock:
                if index != 0:
                    raise VisionError("Chọn MOCK camera index 0.")
                self.mock_connected = True
            else:
                self._adapter().connect(index)
            self.frames.clear()
            return self.status()

    def disconnect(self):
        with self.lock:
            if self.mock:
                self.mock_connected = False
            elif self.adapter:
                self.adapter.disconnect()
            self.frames.clear()
            return self.status()

    def _mock_image(self, calibration):
        if self.mock_preview is None:
            width = min(self.config.get("preview_max_width", 1280), calibration.width)
            height = round(width * calibration.height / calibration.width)
            image = np.full((height, width, 3), (30, 38, 46), dtype=np.uint8)
            for x in range(0, width, 80):
                cv2.line(image, (x, 0), (x, height - 1), (65, 77, 90), 1)
            for y in range(0, height, 80):
                cv2.line(image, (0, y), (width - 1, y), (65, 77, 90), 1)
            cv2.putText(
                image,
                "MOCK CAMERA - NOT A REAL IMAGE",
                (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (60, 210, 245),
                2,
            )
            cv2.drawMarker(
                image, (width // 2, height // 2), (70, 220, 150), cv2.MARKER_CROSS, 50, 2
            )
            self.mock_preview = image
        return self.mock_preview

    def frame(self):
        with self.lock:
            calibration = self._calibration()
            if self.mock:
                if not self.mock_connected:
                    raise VisionError("Camera chưa kết nối.")
                preview = self._mock_image(calibration)
                width, height = calibration.width, calibration.height
            else:
                image = self._adapter().frame()
                height, width = image.shape[:2]
                preview_width = min(width, self.config.get("preview_max_width", 1280))
                preview = cv2.resize(
                    image,
                    (preview_width, round(height * preview_width / width)),
                    interpolation=cv2.INTER_AREA,
                )
            ok, encoded = cv2.imencode(".jpg", preview, [cv2.IMWRITE_JPEG_QUALITY, 85])
            if not ok:
                raise VisionError("Không mã hóa được ảnh camera.")
            frame_id = uuid.uuid4().hex
            metadata = dict(
                frame_id=frame_id,
                width=width,
                height=height,
                captured_at=time.time(),
                fingerprint=calibration.fingerprint,
            )
            self.frames[frame_id] = metadata
            while len(self.frames) > 64:
                self.frames.popitem(last=False)
            return {
                **metadata,
                "preview_width": preview.shape[1],
                "preview_height": preview.shape[0],
                "resolution_matches_calibration": (width, height)
                == (calibration.width, calibration.height),
                "image_data": "data:image/jpeg;base64," + base64.b64encode(encoded).decode("ascii"),
            }

    def convert(self, frame_id, u, v, plane_z_mm):
        with self.lock:
            calibration = self._calibration()
            metadata = self.frames.get(frame_id)
            if not metadata or time.time() - metadata["captured_at"] > 60:
                raise VisionError("Frame đã hết hạn; nhấn LIVE rồi chọn lại điểm.")
            if metadata["fingerprint"] != calibration.fingerprint:
                raise VisionError("Calib đã thay đổi; lấy frame mới trước khi chuyển đổi.")
            result = calibration.pixel_to_base(
                u, v, plane_z_mm, metadata["width"], metadata["height"]
            )
            return {
                **result,
                "frame_id": frame_id,
                "captured_at": metadata["captured_at"],
                "mode": "MOCK" if self.mock else "REAL",
            }

    def close(self):
        with self.lock:
            if self.adapter:
                self.adapter.close()
            self.mock_connected = False
            self.frames.clear()
