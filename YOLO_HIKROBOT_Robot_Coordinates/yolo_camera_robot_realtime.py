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


def read_plane_z(value=None):
    if value is not None:
        return value
    while True:
        try:
            return finite_number(input("Nhap Z mat phang trong Robot Base (mm): ").strip())
        except (ValueError, argparse.ArgumentTypeError):
            print("Nhap mot so huu han (mm).")


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
    lines = [f"{axis} = {value:.3f} mm" for axis, value in zip("XYZ", item["xyz"])]
    return lines + [f"{axis} = {value:.3f} deg" if value is not None else f"{axis} = chua thiet lap"
                    for axis, value in zip(("RX", "RY", "RZ"), orientation)]


def render(frame, detections, orientation, quality, page):
    # Resize ONLY the preview. Bboxes and centers remain native calibration pixels.
    height, width = frame.shape[:2]
    scale = min(1100 / width, 900 / height)
    preview = cv2.resize(frame, (round(width * scale), round(height * scale)))
    canvas = np.full((max(850, preview.shape[0]), preview.shape[1] + 480, 3), 24, np.uint8)
    canvas[:preview.shape[0], :preview.shape[1]] = preview
    for index, item in enumerate(detections, 1):
        x1, y1, x2, y2 = [round(n * scale) for n in item["bbox"]]
        center = (round(item["u"] * scale), round(item["v"] * scale))
        cv2.rectangle(canvas, (x1, y1), (x2, y2), (0, 255, 80), 2)
        cv2.drawMarker(canvas, center, (0, 0, 255), cv2.MARKER_CROSS, 22, 2)
        cv2.putText(canvas, f"VAN {index}: {item['name']} {item['confidence']:.2f}",
                    (x1, max(20, y1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, .6, (0, 255, 80), 2)
    pages = max(1, (len(detections) + 1) // 2)
    page = min(page, pages - 1)
    lines = [f"Calib: {quality}", "XYZ: mm / Euler: deg, intrinsic xyz",
             f"Objects: {len(detections)} | page {page + 1}/{pages} (N/P)", "Q / ESC: exit", ""]
    if not detections:
        lines += ["Khong phat hien van."]
    for i in range(page * 2, min(len(detections), page * 2 + 2)):
        item = detections[i]
        lines += [f"VAN {i + 1}: {item['name']}", f"Confidence: {item['confidence']:.3f}",
                  f"Pixel: u={item['u']:.2f}", f"       v={item['v']:.2f}"]
        lines += pose_lines(item, orientation) + [""]
    for row, line in enumerate(lines):
        cv2.putText(canvas, line, (preview.shape[1] + 12, 27 + row * 26),
                    cv2.FONT_HERSHEY_SIMPLEX, .53, (230, 230, 230), 1, cv2.LINE_AA)
    return canvas, page, pages


def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="backslashreplace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--z", type=finite_number, help="Base plane Z in mm; otherwise prompted at startup.")
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
        plane_z = read_plane_z(args.z)
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
        next_print, page = 0.0, 0
        while True:
            calibration.check_frame(frame)
            result = model.predict(source=frame, conf=args.conf, imgsz=args.imgsz,
                                   device=args.device, verbose=False)[0]
            detections = detections_from_result(result, calibration, plane_z)
            now = time.monotonic()
            if now >= next_print:
                print(f"\nDetections: {len(detections)}", flush=True)
                for index, item in enumerate(detections, 1):
                    print(f"Detection {index}:\nClass: {item['name']}\nConfidence: {item['confidence']:.3f}"
                          f"\nBBox: {item['bbox']}\nPixel center: {item['u']:.3f}, {item['v']:.3f}"
                          "\nRobot target:\n" + "\n".join(pose_lines(item, orientation)), flush=True)
                next_print = now + args.print_interval
            display, page, pages = render(frame, detections, orientation, calibration.quality, page)
            cv2.imshow(WINDOW, display)
            key = cv2.waitKey(1) & 0xFF
            if key in (27, ord('q'), ord('Q')) or cv2.getWindowProperty(WINDOW, cv2.WND_PROP_VISIBLE) < 1:
                break
            if key in (ord('n'), ord('N')):
                page = (page + 1) % pages
            elif key in (ord('p'), ord('P')):
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
