import json
from pathlib import Path
import socket
import sys
import threading
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import MockNX100, Variables, make_server, selection
from nx100_client import NX100, WriteUnknown


class DashboardTests(unittest.TestCase):
    def setUp(self):
        self.no_hardware = patch('nx100_client.socket.create_connection', side_effect=AssertionError('No physical devices in tests'))
        self.no_hardware.start()
        self.service = Variables(MockNX100, mock=True)
        self.service.connect('192.168.255.1', 80)

    def tearDown(self):
        self.service.close()
        self.no_hardware.stop()

    def test_types_and_numeric_index(self):
        self.assertEqual(selection('I', '099'), 'I099')
        self.assertEqual(selection('F', '10'), 'R010')
        self.assertEqual(selection('P', 127), 'P127')
        for kind, index in [('S','0'), ('I','I010'), ('I','1.0'), ('I',True), ('I','100'), ('P','128')]:
            with self.subTest(kind=kind,index=index), self.assertRaises(ValueError):
                selection(kind,index)

    def test_connect_sends_no_variable_command_and_selection_sends_no_write(self):
        with patch.object(self.service.client, 'write_and_read') as write:
            self.assertIsNone(self.service.value)
            self.service.choose('I','99',100)
            self.assertEqual(self.service.snapshot()['value'],'0')
            write.assert_not_called()

    def test_realtime_measures_actual_rate_and_stops(self):
        self.service.choose('I','99',0,True)
        time.sleep(.2)
        s = self.service.snapshot()
        self.assertTrue(s['realtime'])
        self.assertGreater(s['metrics']['reads'],5)
        self.assertGreater(s['metrics']['hz'],10)
        self.assertLess(s['metrics']['hz'],150)
        self.assertGreaterEqual(s['metrics']['avg_ms'],7)
        self.service.stop()
        time.sleep(.03)
        before=self.service.snapshot()['metrics']['reads']
        time.sleep(.05)
        self.assertEqual(self.service.snapshot()['metrics']['reads'],before)

    def test_requested_period_is_separate_from_roundtrip(self):
        self.service.choose('I','99',50,True)
        time.sleep(.23)
        s = self.service.snapshot()
        self.assertLess(s['metrics']['hz'],30)
        self.assertLess(s['metrics']['avg_ms'],40)

    def test_manual_write_readback_and_bounds(self):
        self.service.choose('B','9',100)
        for invalid in ['256','-1','2.5','1\rMOVL']:
            with self.assertRaises(ValueError):
                self.service.write('B009',[invalid])
        self.service.write('B009',['255'])
        s=self.service.snapshot()
        self.assertEqual(s['value'],'255')
        self.assertTrue(s['write_result']['matched'])
        self.assertIsNotNone(s['metrics']['write_ms'])

    def test_write_rejected_for_different_variable(self):
        self.service.choose('I','9',100)
        with self.assertRaises(ValueError):
            self.service.write('I010',['1'])

    def test_position_edit_preserves_frame_tool_posture(self):
        self.service.choose('P','9',100)
        self.service.write('P009',['600','100','-185','180','0','90'])
        self.assertEqual(self.service.value,'1,0,600.000,100.000,-185.000,180.00,0.00,90.00,17,0')

    def test_unknown_write_never_retries_and_requires_correct_readback(self):
        self.service.choose('I','9',100)
        with patch.object(self.service.client,'write_and_read',side_effect=WriteUnknown('unknown')) as write:
            with self.assertRaises(WriteUnknown):
                self.service.write('I009',['3'])
            self.assertEqual(write.call_count,1)
            self.assertFalse(self.service.realtime)
        self.service.choose('I','10',100)
        self.assertTrue(self.service.write_unknown)
        with self.assertRaises(ValueError):
            self.service.write('I010',['2'])
        self.service.choose('I','9',100)
        self.assertFalse(self.service.write_unknown)

    def test_errors_stop_polling_after_three_failures(self):
        with patch.object(self.service.client,'read',side_effect=TimeoutError('test timeout')) as read:
            self.service.choose('I','99',0,True)
            deadline=time.monotonic()+1
            while self.service.realtime and time.monotonic()<deadline:
                time.sleep(.01)
            self.assertFalse(self.service.realtime)
            self.assertEqual(read.call_count,3)
            self.assertEqual(self.service.snapshot()['metrics']['errors'],3)

    def test_no_overlapping_poll_and_manual_write(self):
        self.service.choose('I','9',0,True)
        time.sleep(.04)
        client=self.service.client
        active=0
        maximum=0
        guard=threading.Lock()
        original=client.read
        def tracked(name):
            nonlocal active,maximum
            with guard:
                active+=1;maximum=max(maximum,active)
            try:return original(name)
            finally:
                with guard:active-=1
        with patch.object(client,'read',side_effect=tracked):
            self.service.write('I009',['10'])
            time.sleep(.04)
        self.assertEqual(maximum,1)

    def test_http_assets_and_control_origin(self):
        # The patch only blocks outgoing socket.create_connection. Local test HTTP
        # uses a direct socket implementation, never a real controller connection.
        server=make_server(self.service,0)
        worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
        port=server.server_port
        def query(path,body=None,headers=None):
            import http.client
            conn=http.client.HTTPConnection('127.0.0.1',port,timeout=3)
            conn._create_connection=lambda address,timeout,source_address=None: local_socket(address,timeout)
            raw=json.dumps(body) if body is not None else None
            conn.request('POST' if body is not None else 'GET',path,raw,headers or {})
            response=conn.getresponse();result=(response.status,response.read());conn.close();return result
        def local_socket(address,timeout):
            s=socket.socket();s.settimeout(timeout);s.connect(address);return s
        try:
            code,html=query('/')
            self.assertEqual(code,200)
            self.assertIn(b'id="index"',html)
            self.assertEqual(query('/app.js')[0],200)
            self.assertEqual(query('/api/read',{'kind':'I','index':'9'})[0],403)
            headers={'X-NX100-Control':'operator','Content-Type':'application/json'}
            self.assertEqual(query('/api/read',{'kind':'I','index':'9'},headers)[0],200)
            self.assertEqual(query('/api/write',{'name':'I009','values':['42']},headers)[0],200)
            bad=dict(headers,Origin='https://external.example')
            self.assertEqual(query('/api/write',{'name':'I009','values':['99']},bad)[0],403)
            self.assertEqual(self.service.value,'42')
            self.assertEqual(query('/api/read',{'kind':'S','index':'0'},headers)[0],400)
        finally:
            server.shutdown();server.server_close();worker.join(timeout=2)


if __name__=='__main__':
    unittest.main()
