"""Camera snapshot -> swap LAN cable -> manually send saved robot target."""
import os
import sys
from pathlib import Path


def _use_project_python():
    executable = Path(__file__).resolve().parent / '.venv' / 'Scripts' / 'python.exe'
    if executable.is_file() and Path(sys.executable).resolve() != executable.resolve():
        import subprocess
        try:
            raise SystemExit(subprocess.call([str(executable), str(Path(__file__).resolve()), *sys.argv[1:]]))
        except KeyboardInterrupt:
            raise SystemExit(130)


if __name__ == '__main__':
    _use_project_python()

import argparse
import ipaddress
import json
import logging
from logging.handlers import RotatingFileHandler
from contextlib import asynccontextmanager
from urllib.parse import urlsplit

from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field, field_validator

from robot.controller import NX100Controller, ControlError
from vision.calibration import InputError
from vision.pipeline import VisionPipeline, load_calibration
from workflow.snapshot_move import SnapshotMove

BASE = Path(__file__).resolve().parent


class Input(BaseModel):
    model_config = ConfigDict(extra='forbid', allow_inf_nan=False)


class Connection(Input):
    ip: str = '192.168.255.1'
    port: int = Field(default=80, ge=1, le=65535, strict=True)

    @field_validator('ip')
    @classmethod
    def ipv4(cls, value):
        return str(ipaddress.IPv4Address(value))


class CameraInput(Input):
    index: int = Field(default=0, ge=0, strict=True)


class SendInput(Input):
    batch_id: str = Field(min_length=32, max_length=32)
    record_id: str = Field(min_length=32, max_length=32)


class TrackingConfig(Input):
    plane_z_mm: float = Field(ge=-500, le=2500)
    rx: float = Field(ge=-180, le=180)
    ry: float = Field(ge=-180, le=180)
    rz: float = Field(ge=-180, le=180)
    movl_speed: float = Field(ge=.1, le=200)
    confidence: float = Field(gt=0, le=1)
    minimum_move_distance_mm: float = Field(ge=50, le=1000)


class ProcessLease:
    """OS file lock prevents two backend processes owning this project."""
    def __init__(self, path=None):
        self.path = Path(path) if path else BASE / 'logs/controller.lock'

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.file = self.path.open('a+b')
        self.file.seek(0)
        try:
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(self.file.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            self.file.close()
            raise RuntimeError('Another backend owns this project; use one server process')
        return self

    def __exit__(self, *args):
        self.file.close()


def create_app(mock=True, config=None, background=True, storage_dir=None):
    config = config or json.loads((BASE / 'config.json').read_text(encoding='utf-8'))
    TrackingConfig(**config['tracking'])
    robot = NX100Controller(config, mock=mock)
    calibration, calibration_id, calibration_error = None, '', ''
    try:
        calibration, calibration_id = load_calibration(BASE)
    except Exception as exc:
        calibration_error = str(exc)
    storage = Path(storage_dir or BASE / 'data') / ('snapshot_mock.json' if mock else 'snapshot_real.json')
    workflow = SnapshotMove(robot, config, 'MOCK-SYNTHETIC' if mock else calibration_id, storage,
                            calibration_valid=mock or calibration is not None)
    vision = VisionPipeline(BASE, workflow, calibration)

    @asynccontextmanager
    async def lifespan(app):
        with ProcessLease(Path(storage_dir) / 'controller.lock' if storage_dir else None):
            if background:
                robot.start_monitor()
                workflow.start_worker()
            try:
                yield
            finally:
                workflow.close()
                try:
                    vision.close()
                finally:
                    robot.close()

    app = FastAPI(title='NX100 Camera Snapshot Move', lifespan=lifespan, docs_url=None,
                  redoc_url=None, openapi_url=None)
    app.state.robot, app.state.workflow, app.state.vision = robot, workflow, vision

    @app.middleware('http')
    async def protect(request: Request, call_next):
        authority = request.headers.get('host', '')
        try:
            parsed = urlsplit('http://' + authority)
            if (parsed.hostname not in config['web']['allowed_hosts'] or parsed.username
                    or parsed.port != config['web']['port']):
                return JSONResponse({'message': 'Host not authorized'}, status_code=403)
        except ValueError:
            return JSONResponse({'message': 'Invalid host'}, status_code=403)
        origin = request.headers.get('origin')
        if origin and origin != f'{request.url.scheme}://{authority}':
            return JSONResponse({'message': 'Origin rejected'}, status_code=403)
        if request.method not in ('GET', 'HEAD') and (request.headers.get('x-nx100-control') != 'operator'
                or request.headers.get('sec-fetch-site') == 'cross-site'):
            return JSONResponse({'message': 'Operator control header required'}, status_code=403)
        response = await call_next(request)
        response.headers.update({'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff',
            'Content-Security-Policy': "default-src 'self'; connect-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"})
        return response

    @app.exception_handler(ControlError)
    async def control_error(request, exc):
        return JSONResponse({'code': exc.code, 'message': exc.message}, status_code=exc.status)

    @app.exception_handler(InputError)
    async def input_error(request, exc):
        return JSONResponse({'message': str(exc)}, status_code=409)

    @app.exception_handler(RequestValidationError)
    async def validation_error(request, exc):
        return JSONResponse({'message': 'Invalid input', 'detail': str(exc)}, status_code=422)

    @app.get('/')
    def index():
        return FileResponse(BASE / 'templates/index.html')

    @app.get('/api/state')
    def state():
        return dict(robot=robot.snapshot(), workflow=workflow.snapshot(), vision=vision.status(),
                    calibration=dict(quality=calibration.quality if calibration else 'invalid',
                        message=calibration_error, image_size=calibration.size if calibration else None,
                        offset_mm=[280, 215], mode='MOCK SYNTHETIC' if mock else 'REAL',
                        accepted_by_operator=calibration is not None), events=robot.events())

    @app.post('/api/robot/connect')
    def connect(data: Connection):
        return workflow.connect_robot(data.ip, data.port)

    @app.post('/api/robot/disconnect')
    def disconnect():
        return workflow.disconnect_robot()

    @app.post('/api/camera/scan')
    def scan():
        return vision.scan()

    @app.post('/api/camera/connect')
    def camera_connect(data: CameraInput):
        with workflow.lock:
            workflow._busy()
        vision.connect(data.index)
        return vision.status()

    @app.post('/api/camera/disconnect')
    def camera_disconnect():
        vision.disconnect()
        return vision.status()

    @app.get('/api/preview.jpg')
    def preview():
        with vision.lock:
            if vision.preview is None:
                raise HTTPException(404, 'No frame yet')
            return Response(vision.preview, media_type='image/jpeg')

    @app.post('/api/config')
    def configuration(data: TrackingConfig):
        workflow.update_config(data.model_dump())
        return workflow.snapshot()

    @app.post('/api/snapshot/capture')
    def capture():
        return workflow.capture()

    @app.post('/api/snapshot/send')
    def send(data: SendInput):
        return workflow.send(data.batch_id, data.record_id)

    @app.post('/api/fault/acknowledge')
    def acknowledge():
        workflow.acknowledge_fault()
        return workflow.snapshot()

    @app.post('/api/robot/hold')
    def hold():
        return workflow.hold()

    @app.post('/api/robot/hold/release')
    def release_hold():
        return workflow.release_hold()

    app.mount('/static', StaticFiles(directory=BASE / 'static'), name='static')
    return app


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--mock', action='store_true')
    mode.add_argument('--real', action='store_true')
    parser.add_argument('--no-browser', action='store_true')
    args = parser.parse_args()
    (BASE / 'logs').mkdir(exist_ok=True)
    handler = RotatingFileHandler(BASE / 'logs/events.log', maxBytes=2_000_000, backupCount=4, encoding='utf-8')
    handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
    logger = logging.getLogger('nx100.events')
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    import uvicorn
    application = create_app(mock=args.mock)
    port = application.state.workflow.config['web']['port']
    print(f"Mode: {'MOCK' if args.mock else 'REAL'} | http://127.0.0.1:{port}")
    if not args.no_browser:
        import threading
        import webbrowser
        opener = threading.Timer(1.5, lambda: webbrowser.open(f'http://127.0.0.1:{port}'))
        opener.daemon = True
        opener.start()
    uvicorn.run(application, host='0.0.0.0', port=port, workers=1, proxy_headers=False)


if __name__ == '__main__':
    main()
