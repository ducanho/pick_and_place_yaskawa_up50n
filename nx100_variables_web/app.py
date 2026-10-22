"""Local NX100 variable dashboard. Python 3.10+, no third-party packages."""
from __future__ import annotations

import argparse
from collections import deque
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import ipaddress
import json
from pathlib import Path
import re
import statistics
import threading
import time
from urllib.parse import urlsplit
import webbrowser

from nx100_client import NX100, NXError, WriteUnknown, edited_value, editor_data, matches, variable

BASE = Path(__file__).resolve().parent
KINDS = ('I', 'B', 'D', 'R', 'S', 'F', 'P')


def selection(kind, index):
    if kind not in KINDS:
        raise ValueError('Loại biến không hợp lệ.')
    if kind == 'S':
        raise ValueError('S là biến chuỗi. SAVEV/LOADV trong tài liệu NX100 HW0483202 không hỗ trợ S.')
    if isinstance(index, bool) or not re.fullmatch(r'[0-9]{1,3}', str(index)):
        raise ValueError('Số biến chỉ được nhập chữ số, ví dụ 0, 10 hoặc 99.')
    kind = 'R' if kind == 'F' else kind
    return variable(f'{kind}{index}')[2]


def milliseconds(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= 10000:
        raise ValueError('Chu kỳ đọc phải từ 0 đến 10000 ms.')
    return float(value)


class MockNX100:
    def __init__(self, host='', port=80, timeout=3):
        self.values = {}

    def connect(self):
        return 'MOCK — không kết nối robot thật'

    def read(self, name):
        time.sleep(.008)
        return self.values.get(name, '1,0,530.000,0.000,0.000,180.00,0.00,90.00,17,0' if name.startswith('P') else '0')

    def write_and_read(self, name, value):
        self.values[name] = value
        actual = self.read(name)
        return actual, matches(name[0], value, actual)


class Variables:
    def __init__(self, factory=NX100, mock=False):
        self.factory, self.mock = factory, mock
        self.lock, self.io = threading.RLock(), threading.Lock()
        self.closed = threading.Event()
        self.wake = threading.Event()
        self.client = None
        self.connected = self.realtime = False
        self.host, self.port = '192.168.255.1', 80
        self.kind, self.index, self.name = 'I', '99', 'I099'
        self.period_ms = 100.0
        self.generation = 0
        self.value = None
        self.updated_at = None
        self.error = ''
        self.write_result = None
        self.write_unknown = False
        self.uncertain_name = None
        self.write_ms = None
        self.events = deque(maxlen=80)
        self.reset_metrics()
        self.worker = threading.Thread(target=self._loop, name='variable-reader', daemon=True)
        self.worker.start()

    def reset_metrics(self):
        self.samples = deque(maxlen=2000)
        self.reads = self.errors = self.consecutive_errors = 0
        self.started = time.monotonic()
        self.stopped = None

    def event(self, action, message):
        self.events.append({'time': datetime.now().strftime('%H:%M:%S'), 'action': action, 'message': message})

    def connect(self, host, port):
        host = str(ipaddress.IPv4Address(host))
        if isinstance(port, bool) or not str(port).isdigit() or not 1 <= int(port) <= 65535:
            raise ValueError('Port phải từ 1 đến 65535.')
        with self.io:
            with self.lock:
                self.realtime = self.connected = False
                self.generation += 1
                self.value = None
            candidate = self.factory(host, int(port), 3.0)
            banner = candidate.connect()
            with self.lock:
                self.client, self.host, self.port = candidate, host, int(port)
                self.connected = True
                self.error = ''
                self.reset_metrics()
                self.event('CONNECT', banner)

    def disconnect(self):
        with self.io, self.lock:
            self.realtime = self.connected = False
            self.client = None
            self.generation += 1
            self.stopped = time.monotonic()
            self.event('DISCONNECT', 'Đã ngắt kết nối.')

    def choose(self, kind, index, period_ms, realtime=False):
        name = selection(kind, index)
        period_ms = milliseconds(period_ms)
        with self.io, self.lock:
            if not self.connected:
                raise NXError('Chưa kết nối robot.')
            self.generation += 1
            self.kind, self.index, self.name = kind, str(int(index)), name
            self.period_ms = period_ms
            self.realtime = realtime
            self.value = None
            self.updated_at = None
            self.error = ''
            self.write_result = None
            self.write_ms = None
            # An uncertain write must be resolved by a successful read, not selection.
            self.reset_metrics()
            self.event('REALTIME' if realtime else 'READ', f'{name} · chu kỳ {period_ms:g} ms')
        if realtime:
            self.wake.set()
        else:
            self.read_once()

    def stop(self):
        with self.lock:
            self.realtime = False
            self.generation += 1
            self.stopped = time.monotonic()
            self.event('STOP', 'Đã dừng đọc realtime.')
        self.wake.set()

    def read_once(self, generation=None):
        with self.io:
            with self.lock:
                if generation is not None and (generation != self.generation or not self.realtime):
                    return
                if not self.connected or self.client is None:
                    raise NXError('Chưa kết nối robot.')
                current_generation, name, client = self.generation, self.name, self.client
            start = time.perf_counter()
            try:
                value = client.read(name)
            except Exception as exc:
                with self.lock:
                    if current_generation == self.generation:
                        self.errors += 1
                        self.consecutive_errors += 1
                        self.error = str(exc)
                        if self.consecutive_errors >= 3:
                            self.realtime = False
                            self.stopped = time.monotonic()
                            self.error += ' Đã dừng realtime sau 3 lần đọc lỗi liên tiếp.'
                            self.event('ERROR', self.error)
                raise
            elapsed = (time.perf_counter() - start) * 1000
            with self.lock:
                if current_generation == self.generation:
                    self.value, self.error = value, ''
                    self.updated_at = datetime.now(timezone.utc).isoformat()
                    self.reads += 1
                    self.consecutive_errors = 0
                    self.samples.append((time.monotonic(), elapsed))
                    if self.write_unknown and self.uncertain_name == name:
                        self.write_unknown = False
                        self.uncertain_name = None
                        self.event('READBACK', f'Đã đọc lại {name} = {value}. Kiểm tra trước lần ghi tiếp theo.')

    def write(self, name, values):
        if not isinstance(values, list) or any(not isinstance(v, str) for v in values):
            raise ValueError('Giá trị ghi không hợp lệ.')
        with self.io:
            with self.lock:
                if not self.connected or self.value is None or name != self.name:
                    raise ValueError('Cần đọc đúng biến đang chọn trước khi ghi.')
                if self.write_unknown:
                    raise ValueError('Lần ghi trước chưa rõ kết quả. Đọc lại trước khi ghi tiếp.')
                desired = edited_value(name[0], self.value, values)
                client, generation = self.client, self.generation
                self.write_result = None
            started = time.perf_counter()
            try:
                actual, matched = client.write_and_read(name, desired)
            except Exception as exc:
                with self.lock:
                    self.realtime = False
                    self.generation += 1
                    self.stopped = time.monotonic()
                    self.error = str(exc)
                    self.write_unknown = isinstance(exc, WriteUnknown)
                    self.uncertain_name = name if self.write_unknown else None
                    self.event('WRITE ERROR', self.error)
                raise
            with self.lock:
                if generation == self.generation:
                    self.value = actual
                    self.updated_at = datetime.now(timezone.utc).isoformat()
                self.write_ms = (time.perf_counter() - started) * 1000
                self.write_result = {'name': name, 'desired': desired, 'actual': actual, 'matched': matched}
                self.event('WRITE OK' if matched else 'MISMATCH', f'{name}: yêu cầu {desired} · đọc lại {actual}')

    def _loop(self):
        while not self.closed.is_set():
            with self.lock:
                enabled, generation, period = self.realtime, self.generation, self.period_ms
            if not enabled:
                self.wake.wait(.2)
                self.wake.clear()
                continue
            start = time.monotonic()
            try:
                self.read_once(generation)
            except Exception:
                pass  # read_once records errors; writes are never retried.
            self.wake.wait(max(0, period / 1000 - (time.monotonic() - start)))
            self.wake.clear()

    def snapshot(self):
        with self.lock:
            now = time.monotonic() if self.realtime else (self.stopped or time.monotonic())
            recent = [(t, ms) for t, ms in self.samples if 0 <= now - t <= 5]
            elapsed = max(.001, min(5.0, now - self.started))
            durations = [ms for _, ms in recent]
            all_durations = [ms for _, ms in self.samples]
            rate = len(recent) / elapsed if self.realtime or self.stopped else 0.0
            labels, values, info = editor_data(self.name[0], self.value) if self.value is not None else ([], [], '')
            return dict(mode='MOCK' if self.mock else 'REAL', connected=self.connected,
                        host=self.host, port=self.port, kind=self.kind, index=self.index, name=self.name,
                        realtime=self.realtime, period_ms=self.period_ms, value=self.value,
                        labels=labels, values=values, info=info, updated_at=self.updated_at,
                        error=self.error, write_result=self.write_result, write_unknown=self.write_unknown,
                        uncertain_name=self.uncertain_name,
                        metrics=dict(hz=round(rate, 2), reads=self.reads, errors=self.errors,
                                     last_ms=round(self.samples[-1][1], 2) if self.samples else None,
                                     avg_ms=round(statistics.mean(durations or all_durations), 2) if all_durations else None,
                                     p95_ms=round(sorted(durations or all_durations)[max(0, int(len(durations or all_durations)*.95+.999)-1)], 2) if all_durations else None,
                                     write_ms=round(self.write_ms, 2) if self.write_ms is not None else None),
                        events=list(self.events))

    def close(self):
        self.closed.set()
        self.wake.set()
        self.worker.join(timeout=4)


def make_server(service, port=8010):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def reply(self, status, data, content_type='application/json; charset=utf-8'):
            payload = json.dumps(data, ensure_ascii=False).encode('utf-8') if isinstance(data, dict) else data
            try:
                self.send_response(status)
                self.send_header('Content-Type', content_type)
                self.send_header('Content-Length', str(len(payload)))
                self.send_header('Cache-Control', 'no-store')
                self.send_header('X-Content-Type-Options', 'nosniff')
                self.send_header('Content-Security-Policy', "default-src 'self'; style-src 'self'; script-src 'self'; connect-src 'self'; img-src 'self' data:; frame-ancestors 'none'")
                self.end_headers()
                self.wfile.write(payload)
            except ConnectionError:
                pass  # Closing/reloading the browser must not change a completed operation.

        def local(self):
            return self.headers.get('Host') in {f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}'}

        def do_GET(self):
            if not self.local():
                return self.reply(403, {'message': 'Host không hợp lệ.'})
            path = urlsplit(self.path).path
            if path == '/api/state':
                return self.reply(200, service.snapshot())
            assets = {'/': ('index.html', 'text/html; charset=utf-8'),
                      '/app.js': ('app.js', 'text/javascript; charset=utf-8'),
                      '/style.css': ('style.css', 'text/css; charset=utf-8')}
            if path not in assets:
                return self.reply(404, {'message': 'Không tìm thấy.'})
            filename, mime = assets[path]
            self.reply(200, (BASE / 'static' / filename).read_bytes(), mime)

        def do_POST(self):
            origins = {f'http://127.0.0.1:{self.server.server_port}', f'http://localhost:{self.server.server_port}'}
            if not self.local() or self.headers.get('Origin', '') not in origins | {''} or self.headers.get('X-NX100-Control') != 'operator':
                # Drain a small rejected request before closing so Windows does not
                # reset the connection and discard the HTTP error response.
                try:
                    size = int(self.headers.get('Content-Length', '0'))
                    if 0 < size <= 16384:
                        self.connection.settimeout(3)
                        self.rfile.read(size)
                except (ValueError, OSError):
                    pass
                return self.reply(403, {'message': 'Yêu cầu điều khiển không hợp lệ.'})
            try:
                size = int(self.headers.get('Content-Length', '0'))
                if not 0 < size <= 16384:
                    raise ValueError('Kích thước dữ liệu không hợp lệ.')
                data = json.loads(self.rfile.read(size))
                if not isinstance(data, dict):
                    raise ValueError('Cần dữ liệu JSON object.')
                path = urlsplit(self.path).path
                if path == '/api/connect':
                    service.connect(data.get('host', '192.168.255.1'), data.get('port', 80))
                elif path == '/api/disconnect':
                    service.disconnect()
                elif path in ('/api/read', '/api/start'):
                    service.choose(data.get('kind', 'I'), data.get('index', '99'), data.get('period_ms', 100), path.endswith('start'))
                elif path == '/api/stop':
                    service.stop()
                elif path == '/api/write':
                    service.write(data.get('name'), data.get('values'))
                else:
                    return self.reply(404, {'message': 'Không tìm thấy.'})
                self.reply(200, service.snapshot())
            except (ValueError, TypeError, KeyError) as exc:
                self.reply(400, {'message': str(exc)})
            except Exception as exc:
                self.reply(409, {'message': str(exc)})

    return ThreadingHTTPServer(('127.0.0.1', port), Handler)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='NX100 variables HTML dashboard')
    parser.add_argument('--mock', action='store_true')
    parser.add_argument('--no-browser', action='store_true')
    parser.add_argument('--port', type=int, default=8010)
    args = parser.parse_args()
    service = Variables(MockNX100 if args.mock else NX100, mock=args.mock)
    server = make_server(service, args.port)
    url = f'http://127.0.0.1:{server.server_port}'
    print(f'NX100 Variables | {"MOCK" if args.mock else "REAL"} | {url}', flush=True)
    if not args.no_browser:
        threading.Timer(.5, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        service.close()
        server.server_close()
