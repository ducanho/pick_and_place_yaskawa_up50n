import time

from fastapi.testclient import TestClient

from app import create_app


def wait_for(predicate,seconds=10):
    deadline=time.monotonic()+seconds
    while time.monotonic()<deadline:
        if predicate():return
        time.sleep(.05)
    raise AssertionError('Timed out waiting for mock state')


def test_camera_save_unplug_robot_connect_manual_move_and_reload(config,tmp_path):
    app=create_app(mock=True,config=config,storage_dir=tmp_path)
    with TestClient(app,base_url='http://localhost:8000',headers={'X-NX100-Control':'operator'}) as client:
        assert client.get('/').status_code==200
        assert client.post('/api/camera/scan').status_code==200
        assert client.post('/api/camera/connect',json={'index':0}).status_code==200
        wait_for(lambda:len(app.state.workflow.targets)==3)
        assert not app.state.robot.is_connected()
        response=client.post('/api/snapshot/capture')
        assert response.status_code==200,response.text
        saved=response.json()
        assert [v['target']['object_id'] for v in saved['saved']]==[1,2,3]
        assert client.post('/api/camera/disconnect').status_code==200
        assert len(client.get('/api/state').json()['workflow']['saved'])==3
        assert client.post('/api/robot/connect',json={}).status_code==200
        app.state.robot.client.duration=.1
        assert not app.state.robot.active
        command={'batch_id':saved['batch_id'],'record_id':saved['next_record_id']}
        assert client.post('/api/snapshot/send',json=command).status_code==200
        assert client.post('/api/snapshot/send',json=command).status_code==409
        wait_for(lambda:len(app.state.workflow.completed)==1)
        time.sleep(1.1)
        assert not app.state.robot.active
        assert len(app.state.workflow.completed)==1
        assert app.state.workflow.snapshot()['next_object_id']==2
    loaded=create_app(mock=True,config=config,storage_dir=tmp_path,background=False)
    assert len(loaded.state.workflow.completed)==1
    assert loaded.state.workflow.snapshot()['next_object_id']==2
    assert not loaded.state.robot.is_connected()


def test_api_has_no_login_and_protects_origin_and_stale_send(config,tmp_path):
    app=create_app(mock=True,config=config,storage_dir=tmp_path,background=False)
    client=TestClient(app,base_url='http://localhost:8000',headers={'X-NX100-Control':'operator'})
    assert client.get('/api/state').status_code==200
    assert client.post('/api/snapshot/send',json={}).status_code==422
    assert client.post('/api/snapshot/capture',headers={'Origin':'http://wrong.example'}).status_code==403
    assert client.post('/api/snapshot/capture',headers={'X-NX100-Control':''}).status_code==403
    assert client.post('/api/auto/start').status_code==404
    assert client.post('/api/robot/home').status_code==404


def test_mock_and_real_snapshot_files_are_separate(config,tmp_path):
    mock=create_app(mock=True,config=config,storage_dir=tmp_path,background=False)
    real=create_app(mock=False,config=config,storage_dir=tmp_path,background=False)
    assert mock.state.workflow.storage.name=='snapshot_mock.json'
    assert real.state.workflow.storage.name=='snapshot_real.json'
    assert real.state.workflow.calibration_valid
    assert real.state.robot.client is None


def test_release_hold_api_then_ack_has_no_automatic_motion(config,tmp_path):
    app=create_app(mock=True,config=config,storage_dir=tmp_path,background=False)
    client=TestClient(app,base_url='http://localhost:8000',headers={'X-NX100-Control':'operator'})
    assert client.post('/api/robot/connect',json={}).status_code==200
    assert client.post('/api/robot/hold').status_code==200
    result=client.post('/api/robot/hold/release')
    assert result.status_code==200
    assert not result.json()['flags']['hold']
    assert app.state.workflow.fault
    assert client.post('/api/fault/acknowledge').status_code==200
    assert not app.state.workflow.fault and app.state.robot.active is None
