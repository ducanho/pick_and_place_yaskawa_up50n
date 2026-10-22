import json

import pytest

from conftest import item,feed,capture,send_next,complete
from robot.controller import ControlError
from robot.protocol import OutcomeUnknown,ProtocolError
from workflow.snapshot_move import SnapshotMove


def test_new_snapshot_can_revisit_earlier_completed_site(rig):
    r,w,c=capture(rig)
    w.connect_robot('192.168.255.1',80)
    send_next(w);complete(r,w,c)
    feed(w,c,[item(2,(1050,120,100))],count=1)
    w.capture();send_next(w);complete(r,w,c)
    # Changing the cable/session must not blacklist any earlier completed site.
    w.session='new-camera-session'
    feed(w,c,[item(1,(850,120,105))],count=1)
    w.capture()
    assert w.snapshot()['saved'][0]['eligible']
    send_next(w)
    assert r.active and w.active_id
    assert r.snapshot()['motion']['target']['x']==850
    assert len(w.completed)==2


def test_save_works_without_robot_connected(rig):
    r,w,c=capture(rig)
    assert not r.is_connected() and r.client is None
    assert len(w.saved)==1 and w.storage.exists()
    assert w.saved[0].target.xyz==(850,120,100)


def test_robot_fault_does_not_block_camera_save_but_still_blocks_move(rig):
    r,w,c=rig
    w.fault=True
    feed(w,c,count=1)
    assert w.snapshot()['can_capture']
    w.capture()
    assert len(w.saved)==1 and w.fault
    assert json.loads(w.storage.read_text(encoding='utf-8'))['fault'] is True
    w.connect_robot('192.168.255.1',80)
    with pytest.raises(ControlError):send_next(w)
    assert not r.active


def test_camera_startup_error_does_not_hide_motion_fault(rig):
    r,w,c=rig
    w.fault=True;w.message='Motion confirmation timeout'
    w.vision_failed('Camera waiting for first frame')
    assert w.message=='Motion confirmation timeout'
    feed(w,c,count=1)
    assert w.snapshot()['can_capture'] and w.fault


def test_hold_without_connected_robot_does_not_create_fault(rig):
    r,w,c=rig
    with pytest.raises(ControlError):w.hold()
    assert not w.fault


@pytest.mark.parametrize('count',[1,9,10,28])
def test_capture_immediately_with_any_detection_count(rig,count):
    r,w,c=rig;feed(w,c,count=count)
    w.capture()
    assert len(w.saved)==1 and r.active is None


def test_position_changes_can_be_saved_immediately(rig):
    r,w,c=rig;feed(w,c,count=1);w.capture()
    feed(w,c,[item(xyz=(900,120,100))],count=1,start=2)
    w.capture()
    assert w.saved[0].target.xyz==(900,120,100)


@pytest.mark.parametrize('invalid',['missing_xyz','nan','error','bbox','low_confidence'])
def test_detection_must_have_valid_coordinates_to_save(rig,invalid):
    r,w,c=rig;detection=item()
    if invalid=='missing_xyz':detection.pop('xyz')
    elif invalid=='nan':detection['xyz']=(float('nan'),0,0)
    elif invalid=='error':detection['error']='Cannot compute Base coordinates'
    elif invalid=='bbox':detection['bbox']=(10,10,10,10)
    else:detection['confidence']=.1
    w.publish([detection],1,c(),w.version)
    with pytest.raises(ControlError,match='YOLO'):w.capture()
    assert not w.saved and not r.active


def test_saved_coordinates_survive_camera_disconnect_and_age(rig):
    r,w,c=capture(rig)
    original=w.saved[0].target
    w.vision_failed('camera unplugged');c.advance(600)
    assert w.saved[0].target is original
    assert w.snapshot()['next_object_id']==1
    w.connect_robot('192.168.255.1',80)
    send_next(w)
    assert r.active and w.active_id
    assert r.snapshot()['motion']['target']['x']==850


def test_no_motion_on_capture_connect_or_poll(rig):
    r,w,c=capture(rig)
    w.connect_robot('192.168.255.1',80)
    for _ in range(10):c.advance();r.poll_once();w.tick()
    assert r.active is None and w.active_id is None
    assert not w.completed


def test_read_only_reconnect_does_not_need_restart(rig):
    r,w,c=capture(rig)
    w.connect_robot('192.168.255.1',80)
    w.fault=True
    assert w.connect_robot('192.168.255.1',80)['connected']
    assert w.fault and not r.active


def test_manual_sequence_prioritizes_lowest_id_and_never_auto_sends(rig):
    r,w,c=capture(rig,[item(3,(1250,0,100)),item(1),item(2,(1050,0,100))])
    w.vision_failed('expected unplug');w.connect_robot('192.168.255.1',80)
    send_next(w)
    assert w.saved[0].target.object_id==1 and w.saved[0].status=='SENDING'
    with pytest.raises(ControlError):send_next(w)
    assert not w.completed
    c.advance(3.1);r.poll_once();w.tick()
    assert not w.completed  # One position sample cannot confirm completion.
    c.advance(.2);r.poll_once();w.tick()
    assert [v.target.object_id for v in w.completed]==[1]
    assert w.snapshot()['next_object_id']==2 and not r.active
    for _ in range(10):c.advance();r.poll_once();w.tick()
    assert not r.active and len(w.completed)==1
    send_next(w);complete(r,w,c)
    assert [v.target.object_id for v in w.completed]==[1,2]
    send_next(w);complete(r,w,c)
    assert [v.target.object_id for v in w.completed]==[1,2,3]
    with pytest.raises(ControlError):send_next(w)


@pytest.mark.parametrize('distance,allowed',[(20,False),(49,False),(50,False),(51,True)])
def test_strict_fifty_mm_before_next_send(rig,distance,allowed):
    r,w,c=capture(rig,[item(1),item(2,(850+distance,120,100))])
    w.connect_robot('192.168.255.1',80);send_next(w);complete(r,w,c)
    assert bool(w.snapshot()['next_record_id']) is allowed


def test_euclidean_distance_and_processed_track(rig):
    r,w,c=capture(rig,[item(1),item(2,(890,160,100))])
    w.connect_robot('192.168.255.1',80);send_next(w);complete(r,w,c)
    assert w.snapshot()['next_object_id']==2
    send_next(w);complete(r,w,c)
    feed(w,c,[item(1)],start=36)
    w.capture()
    assert len(w.saved)==1  # Saving is unrestricted by completed MOVE distance.
    assert w.snapshot()['next_record_id'] is None  # MOVE still rejects a processed location.


def test_pending_reloads_but_does_not_auto_move(rig):
    r,w,c=capture(rig)
    loaded=SnapshotMove(r,w.config,w.calibration_id,w.storage,clock=c)
    assert loaded.saved[0].target==w.saved[0].target
    loaded.vision_failed('no camera');c.advance(300)
    loaded.connect_robot('192.168.255.1',80)
    loaded.tick();assert r.active is None
    send_next(loaded);assert r.active


def test_inflight_reload_is_uncertain_and_cannot_resend(rig):
    r,w,c=capture(rig);w.connect_robot('192.168.255.1',80);send_next(w)
    loaded=SnapshotMove(r,w.config,w.calibration_id,w.storage,clock=c)
    assert loaded.fault and loaded.saved[0].status=='UNCERTAIN'
    assert loaded.snapshot()['next_record_id'] is None


@pytest.mark.parametrize('word1,word2',[(194,0),(194,80),(194,72),(202,64),(66,64),(162,64)])
def test_real_preflight_conditions_still_required(rig,word1,word2):
    r,w,c=capture(rig);w.connect_robot('192.168.255.1',80)
    r.client.word1,r.client.word2=word1,word2
    with pytest.raises(ControlError):send_next(w)
    assert r.active is None and w.saved[0].status=='SAVED'
    assert not w.completed


def test_configuration_invalidates_unsent_saved_positions(rig):
    r,w,c=capture(rig)
    old_batch=w.batch_id
    w.update_config({'plane_z_mm':150})
    assert not w.saved and not w.targets
    assert w.batch_id is None and old_batch is not None


def test_wrong_or_old_batch_request_rejected(rig):
    r,w,c=capture(rig);w.connect_robot('192.168.255.1',80)
    with pytest.raises(ControlError):w.send('x'*32,w.saved[0].record_id)
    with pytest.raises(ControlError):w.send(w.batch_id,'x'*32)
    assert r.active is None


def test_unknown_move_result_never_retried(rig,monkeypatch):
    r,w,c=capture(rig);w.connect_robot('192.168.255.1',80)
    original=r.client.execute;calls=[]
    def execute(name,data=''):
        if name=='MOVL':calls.append(name);raise OutcomeUnknown('lost acknowledgment')
        return original(name,data)
    monkeypatch.setattr(r.client,'execute',execute)
    with pytest.raises(ControlError):send_next(w)
    assert w.fault and w.saved[0].status=='UNCERTAIN'
    with pytest.raises(ControlError):send_next(w)
    assert calls==['MOVL'] and not w.completed


def test_connection_lost_after_accept_does_not_commit(rig,monkeypatch):
    r,w,c=capture(rig);w.connect_robot('192.168.255.1',80);send_next(w)
    def fail(*args):raise ProtocolError('lost link')
    monkeypatch.setattr(r.client,'execute',fail)
    r.poll_once();w.tick()
    assert w.fault and not w.completed and w.saved[0].status=='UNCERTAIN'


def test_hold_never_sends_home_or_another_move(rig):
    r,w,c=capture(rig);w.connect_robot('192.168.255.1',80);send_next(w)
    w.hold()
    assert w.fault and not w.completed and r.active is None
    assert w.saved[0].status=='UNCERTAIN'


def test_release_hold_then_ack_does_not_resend_interrupted_move(rig):
    r,w,c=capture(rig);w.connect_robot('192.168.255.1',80);send_next(w)
    w.hold();assert r.client.word2 & 8
    result=w.release_hold()
    assert not result['flags']['hold'] and w.fault
    assert r.active is None and r.client.target is None
    assert w.saved[0].status=='UNCERTAIN'
    w.acknowledge_fault()
    assert not w.fault and w.snapshot()['next_record_id'] is None
    assert sum('MOCK MOVL ' in e['message'] for e in r.events())==1


def test_idle_hold_release_ack_restores_manual_send_readiness(rig):
    r,w,c=capture(rig);w.connect_robot('192.168.255.1',80)
    w.hold();w.release_hold()
    assert w.fault and r.active is None
    w.acknowledge_fault()
    assert not w.fault and w.snapshot()['next_record_id'] is not None
    assert not any('MOCK MOVL ' in e['message'] for e in r.events())


def test_command_release_cannot_clear_external_or_pendant_hold(rig):
    r,w,c=capture(rig);w.connect_robot('192.168.255.1',80)
    w.hold();r.client.word2 |= 4 | 2
    result=w.release_hold()
    assert not result['flags']['command_hold']
    assert result['flags']['external_hold'] and result['flags']['pendant_hold']
    assert result['flags']['hold']
    with pytest.raises(ControlError):w.acknowledge_fault()
    assert w.fault and r.active is None


def test_release_is_blocked_when_controller_is_running(rig):
    r,w,c=capture(rig);w.connect_robot('192.168.255.1',80)
    r.client.word1 |= 8
    with pytest.raises(ControlError):w.release_hold()
    assert not any('MOCK HOLD 0' in e['message'] for e in r.events())


def test_save_outside_workspace_but_do_not_move_and_reject_invalid_calibration(rig):
    r,w,c=rig;feed(w,c,[item(xyz=(3000,0,100))])
    w.capture()
    assert len(w.saved)==1 and w.snapshot()['next_record_id'] is None
    w.calibration_valid=False;feed(w,c,start=36)
    with pytest.raises(ControlError):w.capture()


def test_storage_failure_prevents_any_wire_send(rig,monkeypatch):
    r,w,c=capture(rig);w.connect_robot('192.168.255.1',80)
    def fail():raise ControlError('STORAGE_ERROR','disk full')
    monkeypatch.setattr(w,'_persist',fail)
    with pytest.raises(ControlError):send_next(w)
    assert r.active is None and not w.completed


def test_calibration_or_config_changed_after_reload_blocks_old_snapshot(rig):
    r,w,c=capture(rig)
    loaded=SnapshotMove(r,w.config,'different-calibration',w.storage,clock=c)
    assert loaded.snapshot()['next_record_id'] is None


def test_malformed_saved_data_cannot_trigger_move(rig):
    r,w,c=capture(rig)
    document=json.loads(w.storage.read_text(encoding='utf-8'))
    document['saved'][0]['target']['xyz']=[float('nan'),0,0]
    w.storage.write_text(json.dumps(document),encoding='utf-8')
    loaded=SnapshotMove(r,w.config,w.calibration_id,w.storage,clock=c)
    assert loaded.fault and not loaded.saved and not r.active


def test_capture_latest_displayed_coordinates_without_a_frame_age_gate(rig):
    r,w,c=rig;feed(w,c);c.advance(1)
    w.capture()
    assert len(w.saved)==1


def test_new_live_detection_cannot_change_saved_xyz(rig):
    r,w,c=capture(rig)
    frozen=w.saved[0].target
    feed(w,c,[item(xyz=(1000,120,100))],start=36)
    assert w.saved[0].target is frozen and frozen.xyz==(850,120,100)
    w.connect_robot('192.168.255.1',80);send_next(w)
    assert r.snapshot()['motion']['target']['x']==850


def test_completed_history_survives_restart(rig):
    r,w,c=capture(rig);w.connect_robot('192.168.255.1',80);send_next(w);complete(r,w,c)
    loaded=SnapshotMove(r,w.config,w.calibration_id,w.storage,clock=c)
    assert len(loaded.completed)==1
    assert loaded.snapshot()['phase']=='COMPLETE'
    assert loaded.snapshot()['next_record_id'] is None


def test_explicit_fault_ack_does_not_requeue_uncertain_move(rig):
    r,w,c=capture(rig);w.connect_robot('192.168.255.1',80);send_next(w)
    w.hold()
    r.client.word2 &= ~8  # Simulate operator releasing HOLD at the controller.
    w.acknowledge_fault()
    assert not w.fault
    assert w.saved[0].status=='UNCERTAIN'
    assert w.snapshot()['next_record_id'] is None
