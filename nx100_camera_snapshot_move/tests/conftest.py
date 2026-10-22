import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from robot.controller import NX100Controller
from workflow.snapshot_move import SnapshotMove

BASE = Path(__file__).resolve().parents[1]


class Clock:
    def __init__(self): self.value=100.
    def __call__(self): return self.value
    def advance(self,seconds=.1): self.value+=seconds


@pytest.fixture(autouse=True)
def no_real_devices(monkeypatch):
    def denied(*a,**kw): raise AssertionError('Tests must never connect physical robot/camera')
    monkeypatch.setattr('robot.protocol.socket.create_connection',denied)
    monkeypatch.setattr('vision.camera.MvsCamera.connect',denied)


@pytest.fixture
def config(): return json.loads((BASE/'config.json').read_text(encoding='utf-8'))


@pytest.fixture
def rig(config,tmp_path,monkeypatch):
    clock=Clock()
    fake=SimpleNamespace(monotonic=clock,time=lambda:1000+clock())
    monkeypatch.setattr('robot.controller.time',fake)
    monkeypatch.setattr('robot.mock.time',fake)
    robot=NX100Controller(config,mock=True)
    workflow=SnapshotMove(robot,config,'mock-cal',tmp_path/'snapshot_mock.json',clock=clock)
    return robot,workflow,clock


def item(id=1,xyz=(850.,120.,100.)):
    return dict(id=id,instance=id,name='board',confidence=.95,bbox=(10,10,80,80),u=45,v=45,xyz=xyz)


def feed(w,c,items=None,count=35,start=1):
    from copy import deepcopy
    for f in range(start,start+count):
        c.advance()
        w.publish(deepcopy(items or [item()]),f,c(),w.version)


def capture(rig,items=None):
    r,w,c=rig;feed(w,c,items,count=1);w.capture();return r,w,c


def send_next(w):
    state=w.snapshot()
    return w.send(state['batch_id'],state['next_record_id'])


def complete(r,w,c):
    c.advance(3.1);r.poll_once();w.tick()
    c.advance(.2);r.poll_once();w.tick()
