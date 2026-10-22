"""HIKROBOT -> YOLO -> native bbox center -> calibrated Base position (display only)."""
import argparse
import csv
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path


def select_python_environment():
    """Allow this .py entry point to run from an incomplete virtual environment."""
    root = Path(__file__).resolve().parent
    candidates = [sys.executable, getattr(sys, "_base_executable", sys.executable)]
    for folder in (root, root.parent):
        local = folder / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        if local.is_file():
            candidates.append(str(local))
            try:
                base = subprocess.run(
                    [str(local), "-c", "import sys; print(sys._base_executable)"],
                    capture_output=True, text=True, timeout=10,
                )
                if base.returncode == 0:
                    candidates.append(base.stdout.strip())
            except (OSError, subprocess.TimeoutExpired):
                pass
    candidates.append(shutil.which("python"))
    probe = (
        "import cv2, numpy, ultralytics; "
        "assert any(s.strip().startswith('GUI:') and s.split(':',1)[1].strip() != 'NONE' "
        "for s in cv2.getBuildInformation().splitlines())"
    )
    checked = set()
    for executable in candidates:
        if not executable or not Path(executable).is_file():
            continue
        resolved = os.path.normcase(str(Path(executable).resolve()))
        if resolved in checked:
            continue
        checked.add(resolved)
        try:
            result = subprocess.run([executable, "-c", probe], capture_output=True, timeout=30)
        except (OSError, subprocess.TimeoutExpired):
            continue
        if result.returncode != 0:
            continue
        if resolved == os.path.normcase(str(Path(sys.executable).resolve())):
            return
        print(f"Switching to Python with YOLO / OpenCV GUI: {executable}", flush=True)
        try:
            raise SystemExit(subprocess.call([executable, str(Path(__file__).resolve()), *sys.argv[1:]]))
        except KeyboardInterrupt:
            raise SystemExit(130) from None
    print("No Python environment with ultralytics and OpenCV GUI found.", file=sys.stderr)
    print(f'Install with: "{sys.executable}" -m pip install -r "{root / "requirements-realtime.txt"}"',
          file=sys.stderr)
    print("If OpenCV headless is installed, remove it before installing opencv-python.", file=sys.stderr)
    raise SystemExit(1)


if __name__ == "__main__":
    select_python_environment()

import cv2
import numpy as np

from calibration_transform import InputError, PixelToRobot, OUTPUT_OFFSET_X_MM, OUTPUT_OFFSET_Y_MM
from hik_camera import MvsCamera
from board_tracker import BoardTracker

ROOT = Path(__file__).resolve().parent
CALIBRATION = ROOT / "calibration" / "eye_to_hand.npz"
INTRINSIC = ROOT / "calibration" / "camera_intrinsic_2.npz"
WINDOW = "YOLO / HIKROBOT / Robot Base - Q or ESC to exit"


def find_model():
    candidates = sorted((ROOT / "runs").glob("**/weights/best.pt"))
    if not candidates:
        raise InputError("No runs/**/weights/best.pt found.")
    if len(candidates) == 1:
        return candidates[0]
    # Compare validation mAP50-95 where available; never silently choose by filename.
    scored = []
    for path in candidates:
        results = path.parent.parent / "results.csv"
        if not results.is_file():
            raise InputError("Multiple best.pt files without comparable metrics; use --model runs/.../weights/best.pt.")
        with results.open(encoding="utf-8-sig", newline="") as stream:
            rows = [{k.strip(): v for k, v in row.items()} for row in csv.DictReader(stream)]
        scores = [float(row["metrics/mAP50-95(B)"]) for row in rows]
        if not scores or not np.isfinite(scores).all():
            raise InputError(f"Invalid validation metrics: {results}; select --model explicitly.")
        scored.append((max(scores), path))
    return max(scored, key=lambda pair: (pair[0], str(pair[1])))[1]


def finite_number(value):
    number = float(value)
    if not np.isfinite(number):
        raise argparse.ArgumentTypeError("Value must be finite.")
    return number


def detections_from_result(result, calibration, plane_z):
    # Ultralytics boxes.xyxy already refers to result.orig_shape, BEFORE letterbox.
    # Inference receives the full native BGR frame; no manual input resize/undistort.
    if tuple(result.orig_shape) != (calibration.size[1], calibration.size[0]):
        raise InputError("YOLO original image dimensions differ from calibration.")
    detections = []
    for box in result.boxes:
        x1, y1, x2, y2 = map(float, box.xyxy[0].cpu().tolist())
        u, v = (x1 + x2) / 2.0, (y1 + y2) / 2.0
        item = dict(bbox=(x1, y1, x2, y2), u=u, v=v,
                    confidence=float(box.conf[0].item()), name=result.names[int(box.cls[0].item())])
        try:
            item["xyz"] = calibration.convert(u, v, plane_z)
        except (InputError, cv2.error) as exc:
            item["error"] = str(exc)
        detections.append(item)
    return detections


def pose_lines(item, orientation):
    if "error" in item:
        return ["Robot: unavailable", item["error"]]
    lines = [f"{axis} = {value:+.3f} mm" for axis, value in zip("XYZ", item["xyz"])]
    return lines + [f"{axis} = {value:.3f} deg" if value is not None else f"{axis} = chua thiet lap"
                    for axis, value in zip(("RX", "RY", "RZ"), orientation)]


class HeightInput:
    """Mouse/keyboard Z field drawn directly inside the OpenCV window."""
    def __init__(self, value=0.0):
        self.value = value
        self.text = f"{value:g}"
        self.active = self.select_all = False
        self.error = ""
        self.bounds = self.button = None

    def apply(self):
        try:
            value = finite_number(self.text)
        except (ValueError, argparse.ArgumentTypeError):
            self.error = "Nhap so hop le; Z dang dung khong thay doi."
            self.active = True
            return
        self.value = value
        self.text = f"{value:g}"
        self.active = self.select_all = False
        self.error = ""

    def mouse(self, event, x, y, flags, param):
        if event != cv2.EVENT_LBUTTONDOWN:
            return
        def inside(rect):
            return rect and rect[0] <= x <= rect[2] and rect[1] <= y <= rect[3]
        if inside(self.bounds):
            self.active = self.select_all = True
        elif inside(self.button):
            self.apply()
        else:
            self.active = self.select_all = False
            self.text = f"{self.value:g}"
            self.error = ""

    def key(self, key):
        if not self.active or key == 255:
            return False
        if key in (10, 13):
            self.apply()
        elif key == 27:
            self.active = self.select_all = False
            self.text, self.error = f"{self.value:g}", ""
        elif key == 1:  # Ctrl+A
            self.select_all = True
        elif key in (8, 127):
            self.text = "" if self.select_all else self.text[:-1]
            self.select_all = False
        elif chr(key) in "0123456789.+-eE":
            if self.select_all:
                self.text = ""
                self.select_all = False
            if len(self.text) < 20:
                self.text += chr(key)
            self.error = ""
        return True

    def draw(self, canvas, left):
        top = canvas.shape[0] - 88
        self.bounds = (left, top, left + 290, top + 36)
        self.button = (left + 306, top, left + 448, top + 36)
        cv2.putText(canvas, f"CHIEU CAO Z (Base, mm): {self.value:g}", (left, top - 12),
                    cv2.FONT_HERSHEY_SIMPLEX, .56, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.rectangle(canvas, self.bounds[:2], self.bounds[2:], (55, 55, 55), -1)
        cv2.rectangle(canvas, self.bounds[:2], self.bounds[2:],
                      (0, 220, 255) if self.active else (160, 160, 160), 2)
        if self.select_all:
            cv2.rectangle(canvas, (left + 5, top + 4), (left + 282, top + 32), (140, 75, 20), -1)
        cv2.putText(canvas, self.text + ("|" if self.active else ""), (left + 9, top + 25),
                    cv2.FONT_HERSHEY_SIMPLEX, .65, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.rectangle(canvas, self.button[:2], self.button[2:], (55, 105, 45), -1)
        cv2.putText(canvas, "AP DUNG", (left + 318, top + 24), cv2.FONT_HERSHEY_SIMPLEX,
                    .6, (255, 255, 255), 2, cv2.LINE_AA)
        hint = self.error or "Click de nhap / Enter: ap dung / Esc: huy"
        cv2.putText(canvas, hint, (left, top + 59), cv2.FONT_HERSHEY_SIMPLEX,
                    .47, (80, 140, 255) if self.error else (210, 210, 210), 1, cv2.LINE_AA)


def render(frame, detections, orientation, quality, page, height_input=None):
    # Resize ONLY the preview. Bboxes and centers remain native calibration pixels.
    height, width = frame.shape[:2]
    scale = min(1100 / width, 900 / height)
    preview = cv2.resize(frame, (round(width * scale), round(height * scale)))
    canvas = np.full((max(850, preview.shape[0]), preview.shape[1] + 480, 3), 24, np.uint8)
    canvas[:preview.shape[0], :preview.shape[1]] = preview
    for item in detections:
        x1, y1, x2, y2 = [round(n * scale) for n in item["bbox"]]
        center = (round(item["u"] * scale), round(item["v"] * scale))
        cv2.rectangle(canvas, (x1, y1), (x2, y2), (0, 255, 80), 2)
        cv2.drawMarker(canvas, center, (0, 0, 255), cv2.MARKER_CROSS, 22, 2)
        cv2.putText(canvas, f"ID {item['id']:03d}: {item['name']} {item['confidence']:.2f}",
                    (x1, max(20, y1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, .6, (0, 255, 80), 2)
    pages = max(1, (len(detections) + 1) // 2)
    page = min(page, pages - 1)
    lines = [f"Calib: {quality}", "XYZ: mm / Euler: deg, intrinsic xyz",
             f"Objects: {len(detections)} | page {page + 1}/{pages} (N/P)", "Q / ESC: exit", ""]
    if not detections:
        lines += ["Khong phat hien van."]
    for i in range(page * 2, min(len(detections), page * 2 + 2)):
        item = detections[i]
        lines += [f"ID {item['id']:03d}: {item['name']}", f"Confidence: {item['confidence']:.3f}",
                  f"Pixel: u={item['u']:.2f}", f"       v={item['v']:.2f}"]
        lines += pose_lines(item, orientation) + [""]
    for row, line in enumerate(lines):
        left, baseline = preview.shape[1] + 12, 27 + row * 26
        if line.startswith(tuple(f"{axis} = " for axis in ("X", "Y", "Z", "RX", "RY", "RZ"))):
            axis, value = line.split(" = ", 1)
            cv2.putText(canvas, axis, (left, baseline), cv2.FONT_HERSHEY_SIMPLEX,
                        .62, (255, 255, 255), 2, cv2.LINE_AA)
            # Draw both strokes explicitly so '=' stays distinct from a minus sign.
            for dy in (-11, -5):
                cv2.line(canvas, (left + 46, baseline + dy), (left + 62, baseline + dy),
                         (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(canvas, value, (left + 78, baseline), cv2.FONT_HERSHEY_SIMPLEX,
                        .62, (255, 255, 255), 2, cv2.LINE_AA)
        else:
            cv2.putText(canvas, line, (left, baseline), cv2.FONT_HERSHEY_SIMPLEX,
                        .53, (230, 230, 230), 1, cv2.LINE_AA)
    if height_input is not None:
        height_input.draw(canvas, preview.shape[1] + 12)
    return canvas, page, pages


def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="backslashreplace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--z", type=finite_number, default=0.0, help="Base plane Z in mm; default: 0 (no prompt).")
    parser.add_argument("--orientation", nargs=3, type=finite_number, metavar=("RX", "RY", "RZ"),
                        default=(180.0, 0.0, 90.0),
                        help="Target Euler angles in degrees, intrinsic xyz; default: 180 0 90.")
    parser.add_argument("--model", type=Path, help="Model path relative to this script's directory.")
    parser.add_argument("--camera-index", type=int, default=0)
    parser.add_argument("--sdk-root", type=Path, help="Installed MVS Development directory.")
    parser.add_argument("--conf", type=finite_number, default=.25)
    parser.add_argument("--imgsz", type=int, default=960)
    parser.add_argument("--device", default=None, help="Ultralytics inference device, e.g. cpu or 0.")
    parser.add_argument("--print-interval", type=finite_number, default=1.0, help="Seconds between terminal reports; 0 = every frame.")
    parser.add_argument("--check", action="store_true", help="Load calibration/model and inspect SDK without connecting camera.")
    args = parser.parse_args()
    if not 0 < args.conf <= 1 or args.imgsz <= 0 or args.print_interval < 0:
        parser.error("Require 0 < conf <= 1, imgsz > 0 and print-interval >= 0.")
    camera = None
    window_created = False
    try:
        print(f"PYTHON: {sys.executable}")
        model_path = (ROOT / args.model).resolve() if args.model else find_model()
        if not model_path.is_file():
            raise InputError(f"Model not found: {model_path}")
        calibration = PixelToRobot(CALIBRATION)
        # Confirm copied intrinsic is exactly the one embedded in the existing transform.
        with np.load(INTRINSIC, allow_pickle=False) as intrinsic:
            if (not np.array_equal(intrinsic["K"], calibration.K)
                    or not np.array_equal(intrinsic["distortion"].ravel(), calibration.distortion)
                    or (int(intrinsic["image_width"]), int(intrinsic["image_height"])) != calibration.size):
                raise InputError("Copied intrinsic differs from eye-to-hand intrinsic.")
        print(f"MODEL:\n{model_path}\n\nCALIBRATION:\nIntrinsic: {INTRINSIC}\nEye-to-Hand: {CALIBRATION}")
        print(calibration.quality_message())
        print(f"Native image: {calibration.size}; Base correction "
              f"X {OUTPUT_OFFSET_X_MM:+g} mm, Y {OUTPUT_OFFSET_Y_MM:+g} mm.")
        try:
            from ultralytics import YOLO
        except ImportError as exc:
            raise InputError(
                "Missing ultralytics in this Python environment. "
                "Run this .py file directly to select a ready Python, or install dependencies with: "
                f'"{sys.executable}" -m pip install -r requirements-realtime.txt'
            ) from exc
        gui = next((line.split(":", 1)[1].strip() for line in cv2.getBuildInformation().splitlines()
                    if line.strip().startswith("GUI:")), "UNKNOWN")
        print(f"OpenCV GUI: {gui}")
        if gui == "NONE":
            raise InputError(
                "OpenCV in this environment has no GUI (headless). Run this .py file directly, "
                "or remove opencv-python-headless and install opencv-python in this environment."
            )
        model = YOLO(str(model_path))
        print(f"Model classes: {model.names}")
        camera = MvsCamera(args.sdk_root)
        if args.check:
            print(f"MVS SDK: {camera.status()}")
            print("Calibration and model loaded. No camera stream opened.")
            return 0
        plane_z = args.z
        height_input = HeightInput(plane_z)
        orientation = args.orientation
        print(f"Z plane: {plane_z:.3f} mm; orientation: {orientation}")
        print(f"Cameras: {camera.enumerate()}")
        camera.connect(args.camera_index)
        print("Camera connected.")
        # The existing adapter starts its acquisition thread asynchronously.
        deadline = time.monotonic() + 5
        while True:
            try:
                frame = camera.frame()
                break
            except InputError:
                if camera.error or time.monotonic() >= deadline:
                    raise
                time.sleep(.03)
        cv2.namedWindow(WINDOW, cv2.WINDOW_NORMAL)
        window_created = True
        cv2.resizeWindow(WINDOW, 1500, 850)
        cv2.setMouseCallback(WINDOW, height_input.mouse)
        next_print, page = 0.0, 0
        tracker = BoardTracker(missing_timeout=10.0)
        while True:
            calibration.check_frame(frame)
            result = model.predict(source=frame, conf=args.conf, imgsz=args.imgsz,
                                   device=args.device, verbose=False)[0]
            detections = detections_from_result(result, calibration, height_input.value)
            now = time.monotonic()
            detections = tracker.update(detections, now)
            if now >= next_print:
                print(f"\nDetections: {len(detections)}", flush=True)
                for item in detections:
                    print(f"ID {item['id']:03d}:\nClass: {item['name']}\nConfidence: {item['confidence']:.3f}"
                          f"\nBBox: {item['bbox']}\nPixel center: {item['u']:.3f}, {item['v']:.3f}"
                          "\nRobot target:\n" + "\n".join(pose_lines(item, orientation)), flush=True)
                next_print = now + args.print_interval
            display, page, pages = render(frame, detections, orientation, calibration.quality, page, height_input)
            cv2.imshow(WINDOW, display)
            key = cv2.waitKey(1) & 0xFF
            if cv2.getWindowProperty(WINDOW, cv2.WND_PROP_VISIBLE) < 1:
                break
            consumed = height_input.key(key)
            if height_input.value != plane_z:
                plane_z = height_input.value
                next_print = 0.0
                print(f"Z plane updated: {plane_z:.3f} mm", flush=True)
            if not consumed and key in (27, ord('q'), ord('Q')):
                break
            if not consumed and key in (ord('n'), ord('N')):
                page = (page + 1) % pages
            elif not consumed and key in (ord('p'), ord('P')):
                page = (page - 1) % pages
            frame = camera.frame()
        return 0
    except (InputError, OSError, cv2.error, EOFError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 0
    finally:
        if camera is not None:
            try:
                camera.close()
            except (InputError, OSError) as exc:
                print(f"Camera cleanup: {exc}", file=sys.stderr)
        if window_created:
            try:
                cv2.destroyAllWindows()
            except cv2.error as exc:
                print(f"Window cleanup: {exc}", file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
