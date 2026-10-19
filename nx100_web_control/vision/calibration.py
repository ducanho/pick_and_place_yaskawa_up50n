"""Undistort a raw sensor pixel, then intersect its BASE ray with Z=plane_z."""

import hashlib
import json
import math
from pathlib import Path

import cv2
import numpy as np


class VisionError(ValueError):
    pass


class Calibration:
    def __init__(self, path):
        self.path = Path(path).resolve()
        data = self.path.read_bytes()
        self.report = json.loads(data)
        self.fingerprint = hashlib.sha256(data).hexdigest()
        report = self.report
        if report.get("units", {}).get("translation") != "mm":
            raise VisionError("Calib phải khai báo translation=mm.")
        if report.get("T_base_camera_definition") != "Camera -> robot Base":
            raise VisionError("Chưa xác nhận chiều ma trận Camera -> robot Base.")
        self.T = np.asarray(report["T_base_camera"], dtype=np.float64)
        self.K = np.asarray(report["K"], dtype=np.float64)
        self.distortion = np.asarray(report["distortion"], dtype=np.float64).reshape(-1)
        if self.T.shape != (4, 4) or self.K.shape != (3, 3):
            raise VisionError("T_base_camera phải 4x4, K phải 3x3.")
        if not all(np.isfinite(a).all() for a in [self.T, self.K, self.distortion]):
            raise VisionError("Calib chứa NaN/Inf.")
        rotation = self.T[:3, :3]
        if (
            not np.allclose(self.T[3], [0, 0, 0, 1], atol=1e-8)
            or not np.allclose(rotation.T @ rotation, np.eye(3), atol=1e-6)
            or not np.isclose(np.linalg.det(rotation), 1, atol=1e-6)
        ):
            raise VisionError("T_base_camera không phải rigid transform hợp lệ.")
        if (
            self.K[0, 0] <= 0
            or self.K[1, 1] <= 0
            or not np.allclose(self.K[2], [0, 0, 1])
            or not np.isclose(self.K[0, 1], 0)
            or not np.isclose(self.K[1, 0], 0)
        ):
            raise VisionError("K không đúng mô hình OpenCV pinhole.")
        if self.distortion.size not in (4, 5, 8, 12, 14):
            raise VisionError("Distortion không đúng định dạng OpenCV.")
        self.width, self.height = int(report["image_width"]), int(report["image_height"])
        if self.width <= 0 or self.height <= 0:
            raise VisionError("Kích thước ảnh calib không hợp lệ.")

    def summary(self):
        diagnostics = self.report.get("diagnostics", {})
        return dict(
            path=str(self.path),
            fingerprint=self.fingerprint,
            quality_status=self.report.get("quality_status", "unknown"),
            image_width=self.width,
            image_height=self.height,
            units="mm",
            frame="BASE",
            samples_used=self.report.get("samples_used"),
            residual_summary=diagnostics.get("residual_summary", {}),
            warnings=diagnostics.get("warnings", []),
            T_base_camera=self.T.tolist(),
            K=self.K.tolist(),
            distortion=self.distortion.tolist(),
        )

    def pixel_to_base(self, u, v, plane_z_mm, frame_width, frame_height):
        if (frame_width, frame_height) != (self.width, self.height):
            raise VisionError(
                "Frame khác độ phân giải calib; kiểm tra ROI/binning/camera. Không tự scale K."
            )
        if not all(math.isfinite(float(value)) for value in (u, v, plane_z_mm)):
            raise VisionError("Pixel và Z phải hữu hạn.")
        if not (0 <= u < self.width and 0 <= v < self.height):
            raise VisionError("Pixel ngoài ảnh gốc.")
        normalized = cv2.undistortPointsIter(
            np.array([[[u, v]]], dtype=np.float64),
            self.K,
            self.distortion,
            None,
            None,
            (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 50, 1e-12),
        ).reshape(2)
        direction_camera = np.array([*normalized, 1.0])
        origin = self.T[:3, 3]
        direction = self.T[:3, :3] @ direction_camera
        if abs(direction[2]) < 1e-9:
            raise VisionError("Tia nhìn song song mặt phẳng Z; không có giao điểm duy nhất.")
        camera_z = (plane_z_mm - origin[2]) / direction[2]
        if camera_z <= 0:
            raise VisionError("Mặt phẳng được nhập nằm phía sau camera theo tia nhìn này.")
        camera_point = direction_camera * camera_z
        point = origin + camera_z * direction
        if not np.isfinite(point).all() or np.max(np.abs(point)) > 9_999_999:
            raise VisionError("Giao điểm không hữu hạn hoặc vượt phạm vi biểu diễn.")
        return dict(
            pixel={"u": u, "v": v},
            base_mm=dict(zip(("x", "y", "z"), point.tolist(), strict=True)),
            camera_mm=dict(zip(("x", "y", "z"), camera_point.tolist(), strict=True)),
            plane_z_mm=plane_z_mm,
            frame="BASE",
            units="mm",
            method="undistorted ray intersected with BASE Z plane",
            calibration_fingerprint=self.fingerprint,
            quality_status=self.report.get("quality_status", "unknown"),
            accuracy_validated=False,
        )
