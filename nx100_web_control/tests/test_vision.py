"""Geometry and read-only camera API. No physical camera or robot access."""

import json
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fastapi.testclient import TestClient  # noqa: E402

from app import create_app  # noqa: E402
from vision.calibration import Calibration, VisionError  # noqa: E402
from vision.camera import VisionService  # noqa: E402


def report():
    return dict(
        T_base_camera=[[1, 0, 0, 100], [0, -1, 0, 200], [0, 0, -1, 1000], [0, 0, 0, 1]],
        K=[[800, 0, 320], [0, 800, 240], [0, 0, 1]],
        distortion=[-0.1, 0.01, 0.002, -0.003, 0],
        image_width=640,
        image_height=480,
        units={"translation": "mm"},
        T_base_camera_definition="Camera -> robot Base",
        quality_status="needs_review",
        samples_used=22,
        diagnostics={"residual_summary": {"outlier_count": 22}},
    )


class GeometryTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.path = Path(self.folder.name) / "calibration.json"
        self.path.write_text(json.dumps(report()), encoding="utf-8")
        self.calib = Calibration(self.path)

    def test_center_uses_camera_to_base_direction_and_mm(self):
        result = self.calib.pixel_to_base(320, 240, 100, 640, 480)
        self.assertTrue(np.allclose(list(result["base_mm"].values()), [100, 200, 100]))
        self.assertEqual(result["quality_status"], "needs_review")
        self.assertFalse(result["accuracy_validated"])

    def test_distorted_projection_round_trip_on_translated_plane(self):
        base = np.array([250.0, 100.0, 125.0])
        camera = np.linalg.inv(self.calib.T) @ np.r_[base, 1]
        uv = cv2.projectPoints(
            camera[:3].reshape(1, 3), np.zeros(3), np.zeros(3), self.calib.K, self.calib.distortion
        )[0].reshape(2)
        result = self.calib.pixel_to_base(*uv, 125, 640, 480)
        self.assertTrue(np.allclose(list(result["base_mm"].values()), base, atol=1e-6))

    def test_rejects_invalid_pixel_resolution_and_plane_behind_camera(self):
        for args in [
            (-1, 0, 100, 640, 480),
            (640, 0, 100, 640, 480),
            (320, 240, 100, 320, 240),
            (320, 240, 1100, 640, 480),
            (320, 240, float("nan"), 640, 480),
        ]:
            with self.subTest(args=args), self.assertRaises(VisionError):
                self.calib.pixel_to_base(*args)

    def test_parallel_ray_rejected(self):
        data = report()
        data["T_base_camera"] = [[0, 0, 1, 100], [0, 1, 0, 200], [-1, 0, 0, 1000], [0, 0, 0, 1]]
        self.path.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaisesRegex(VisionError, "song song"):
            Calibration(self.path).pixel_to_base(320, 240, 0, 640, 480)

    def test_bad_transform_or_units_rejected(self):
        for field, value in [
            ("units", {"translation": "m"}),
            ("T_base_camera", np.eye(3).tolist()),
            ("T_base_camera_definition", "Base -> Camera"),
        ]:
            data = report()
            data[field] = value
            self.path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(VisionError):
                Calibration(self.path)

    def test_frames_expire_and_reload_invalidates_old_clicks(self):
        service = VisionService({"calibration_file": str(self.path)}, mock=True)
        service.connect(0)
        frame = service.frame()
        result = service.convert(frame["frame_id"], 320, 240, 100)
        self.assertEqual(result["base_mm"]["z"], 100)
        service.frames[frame["frame_id"]]["captured_at"] = time.time() - 61
        with self.assertRaises(VisionError):
            service.convert(frame["frame_id"], 320, 240, 100)
        frame = service.frame()
        service.reload()
        with self.assertRaises(VisionError):
            service.convert(frame["frame_id"], 320, 240, 100)


class VisionAPITests(unittest.TestCase):
    def test_camera_click_has_no_robot_commands_and_requires_explicit_z(self):
        app = create_app(mock=True)
        client = TestClient(app, base_url="http://127.0.0.1:8000")
        headers = {"X-NX100-Control": "local"}
        with patch.object(
            app.state.robot, "move_cartesian", side_effect=AssertionError("No motion")
        ):
            self.assertEqual(client.get("/camera").status_code, 200)
            status = client.get("/api/vision/status").json()
            self.assertIsNotNone(status["calibration"])
            self.assertIsNone(status["plane_z_mm"])
            self.assertFalse(status["camera"]["connected"])
            self.assertEqual(client.get("/api/vision/frame").status_code, 422)
            self.assertEqual(
                client.post("/api/vision/enumerate", json={}, headers=headers).status_code, 200
            )
            self.assertEqual(
                client.post("/api/vision/connect", json={"index": 0}, headers=headers).status_code,
                200,
            )
            frame = client.get("/api/vision/frame").json()
            self.assertEqual(frame["width"], 5472)
            body = {"frame_id": frame["frame_id"], "u": 2700, "v": 1800}
            self.assertEqual(
                client.post("/api/vision/pixel-to-base", json=body, headers=headers).status_code,
                422,
            )
            body["plane_z_mm"] = 100
            result = client.post("/api/vision/pixel-to-base", json=body, headers=headers)
            self.assertEqual(result.status_code, 200)
            self.assertAlmostEqual(result.json()["base_mm"]["z"], 100)
            self.assertEqual(result.json()["quality_status"], "needs_review")
            self.assertFalse(app.state.robot.is_connected())
            self.assertEqual(
                client.post("/api/vision/disconnect", json={}, headers=headers).status_code, 200
            )
            self.assertEqual(
                client.post("/api/vision/pixel-to-base", json=body, headers=headers).status_code,
                422,
            )
