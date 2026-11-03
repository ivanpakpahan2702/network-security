"""Regresi perilaku lab baru: state, bukti, transaksi, protokol, dan input sah."""
import hashlib
import hmac
import json
import re
import struct
import tempfile
import unittest
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from flask import template_rendered
from labcore.catalog import LABS
from labcore.database import connect
from labcore.factory import create_app
from labcore.protocols import DEMO_KEY, b64url, capture_bytes, checksum, demo_token, read_pcap, verify_token


class AdvancedTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.apps, self.clients = {}, {}

    def client(self, number):
        if number not in self.clients:
            lab = LABS[number - 1]
            self.apps[number] = create_app(lab['id'], data_dir=Path(self.temp.name) / lab['id'], testing=True)
            self.clients[number] = self.apps[number].test_client()
        return self.clients[number]

    def run_lab(self, number, mode='secure', data=None):
        lab = LABS[number - 1]
        client = self.client(number)
        page = client.get('/', base_url=lab['url'])
        token = re.search(r'name="_lab_token" value="([^"]+)"', page.text)[1]
        contexts = []
        def capture(sender, template, context, **extra):
            contexts.append(context)
        with template_rendered.connected_to(capture, self.apps[number]):
            response = client.post('/run/' + mode, base_url=lab['url'], data={**(lab['attack'] if data is None else data), '_lab_token': token})
        return response.status_code, contexts[-1]['result']

    def test_every_new_scenario_and_normal_input(self):
        denied = {16:400,17:403,20:403,21:403,22:403,23:403,25:403,26:403,30:400,31:400,32:403,33:403,36:400,39:403}
        for lab in LABS[14:]:
            for mode in ('vulnerable', 'secure'):
                with self.subTest(lab=lab['id'], mode=mode):
                    status, result = self.run_lab(lab['number'], mode)
                    self.assertEqual(status, denied.get(lab['number'], 200) if mode == 'secure' else 200)
                    self.assertTrue(result['title'])
                    self.assertEqual(self.run_lab(lab['number'], mode, lab['normal'])[0], 200)

    def test_database_parameters_preserve_symbols_and_unicode(self):
        self.client(1)
        value = "quote' question? percent% backslash\\ unicode雪"
        with connect(self.apps[1].config['DATABASE']) as db:
            row = db.execute("SELECT ? AS payload, '?' AS literal, '100%' AS pct",(value,)).fetchone()
            self.assertEqual(dict(row),{'payload':value,'literal':'?','pct':'100%'})
            self.assertEqual(db.execute("SELECT 'raw?%' AS payload").fetchone()[0],'raw?%')

    def test_subnet_prefix_and_point_to_point(self):
        _, result = self.run_lab(15, data={'interface':'192.168.10.10/26','peer':'192.168.10.100'})
        self.assertFalse(result['rows'][0]['peer satu subnet'])
        self.assertEqual(result['rows'][0]['jumlah host'], 62)
        for prefix, hosts in ((31,2),(32,1)):
            _, result = self.run_lab(15, data={'interface':f'10.0.0.0/{prefix}','peer':'10.0.0.0'})
            self.assertEqual(result['rows'][0]['jumlah host'], hosts)
        self.assertEqual(self.run_lab(15, data={'interface':'10.0.0.1/99','peer':'x'})[0],400)

    def test_tcp_requires_ordered_handshake(self):
        self.assertEqual(self.run_lab(16)[0],400)
        self.assertEqual(self.run_lab(16, data=LABS[15]['normal'])[0],200)

    def test_rejected_network_messages_do_not_change_secure_state(self):
        for number in (17,22,23):
            self.assertEqual(self.run_lab(number)[0],403)
            with connect(self.apps[number].config['DATABASE']) as db:
                self.assertEqual(db.execute("SELECT COUNT(*) FROM exercise_state WHERE mode='secure'").fetchone()[0],0)
            self.assertEqual(self.run_lab(number, data=LABS[number-1]['normal'])[0],200)

    def test_http_sensitive_values_are_not_in_secure_trace(self):
        raw = 'POST /login?token=TOPSECRET HTTP/1.1\r\nHost: lab.test\r\nAuthorization: Bearer TOPSECRET\r\nCookie: sid=TOPSECRET\r\n\r\npassword=TOPSECRET'
        # Field name is taken from the public form schema; assertions target leaked data.
        field = LABS[17]['fields'][0]['name']
        _, vulnerable = self.run_lab(18,'vulnerable',{field:raw})
        _, secure = self.run_lab(18,'secure',{field:raw})
        self.assertIn('TOPSECRET',json.dumps(vulnerable))
        self.assertNotIn('TOPSECRET',json.dumps(secure))

    def test_route_uses_longest_prefix(self):
        _, result = self.run_lab(24,data={'destination':'10.20.1.50'})
        self.assertIn('10.20.1.0/24', result['trace'])
        _, result = self.run_lab(24,data={'destination':'203.0.113.8'})
        self.assertIn('0.0.0.0/0',result['trace'])

    def test_pcap_file_structure_checksums_and_analysis(self):
        data = capture_bytes('normal')
        self.assertEqual(struct.unpack('<IHHIIII',data[:24]),(0xa1b2c3d4,2,4,0,0,65535,1))
        offset = 24
        while offset < len(data):
            sec, usec, captured, original = struct.unpack('<IIII',data[offset:offset+16])
            self.assertEqual(captured,original)
            frame = data[offset+16:offset+16+captured]
            ip = frame[14:34]
            self.assertEqual(checksum(ip),0)
            tcp = frame[34:]
            pseudo = ip[12:20] + struct.pack('!BBH',0,6,len(tcp))
            self.assertEqual(checksum(pseudo+tcp),0)
            offset += 16+captured
        self.assertEqual([row['flags'] for row in read_pcap(data)],['SYN','SYN-ACK','ACK'])
        _, result = self.run_lab(27,data={'capture':'normal'})
        self.assertIn('Handshake lengkap: 1',result['detail'])
        self.assertIn('tidak ada',result['detail'])
        _, result = self.run_lab(27,data={'capture':'scan'})
        self.assertIn('192.0.2.10',result['detail'])
        _, result = self.run_lab(27,data={'capture':'incomplete'})
        self.assertIn('Handshake lengkap: 0',result['detail'])
        self.assertIn('tidak ada',result['detail'])
        response = self.client(27).get('/artifacts/normal.pcap')
        self.assertEqual(response.data,data)
        self.assertIn('attachment',response.headers['Content-Disposition'])
        response.close()
        self.assertEqual(self.client(27).get('/artifacts/unknown.pcap').status_code,404)
        with self.assertRaises(ValueError):
            read_pcap(b'invalid')

    def test_ids_metrics_show_false_positive_and_missed_attack(self):
        _, initial = self.run_lab(28,'vulnerable',{'threshold':'4'})
        _, improved = self.run_lab(28,'secure',{'threshold':'4'})
        self.assertGreater(initial['rows'][0]['FP'],improved['rows'][0]['FP'])
        self.assertEqual(improved['rows'][0]['TP'],1)
        self.assertEqual(improved['rows'][0]['FP'],0)
        _, missed = self.run_lab(28,'secure',{'threshold':'7'})
        self.assertEqual(missed['rows'][0]['FN'],1)

    def test_siem_window_and_account_change_correlation(self):
        _, result = self.run_lab(29,data={'account':'alice','window':'15'})
        self.assertIn('1 rantai',result['detail'])
        for data in ({'account':'alice','window':'1'},{'account':'bob','window':'15'}):
            _, result = self.run_lab(29,data=data)
            self.assertIn('0 rantai',result['detail'])

    def test_incident_workflow_and_capstone_evidence(self):
        self.assertEqual(self.run_lab(30)[0],400)
        _, result = self.run_lab(30,data=LABS[29]['normal'])
        self.assertEqual(result['grade'],100)
        response = self.client(30).get('/artifacts/evidence.json')
        self.assertIn(hashlib.sha256(response.data).hexdigest(),result['trace'])
        evidence = response.json
        self.assertEqual({row['id'] for row in evidence},{'E01','E02','E03','E04','E05'})
        _, incomplete = self.run_lab(40)
        _, complete = self.run_lab(40,data=LABS[39]['normal'])
        self.assertLess(incomplete['grade'],100)
        self.assertEqual(complete['grade'],100)
        self.assertTrue(all(row['lulus'] for row in complete['rows']))

    def test_jwt_claims_signature_algorithm_and_types(self):
        token = demo_token()
        self.assertEqual(verify_token(token)['role'],'user')
        head, body, signature = token.split('.')
        for changes in ({'exp':1},{'aud':'other'},{'iss':'other'},{'role':[]},{'exp':True}):
            from labcore.protocols import decode64
            claims = json.loads(decode64(body))
            claims.update(changes)
            unsigned = head+'.'+b64url(json.dumps(claims).encode())
            altered = unsigned+'.'+b64url(hmac.digest(DEMO_KEY,unsigned.encode(),'sha256'))
            with self.assertRaises(ValueError):
                verify_token(altered)
        with self.assertRaises(ValueError):
            verify_token(head+'.'+body+'.'+b64url(b'not-a-signature'))
        with self.assertRaises(ValueError):
            verify_token(demo_token(True))

    def test_mass_assignment_cannot_promote_secure_profile(self):
        self.assertEqual(self.run_lab(32,'vulnerable')[0],200)
        self.assertEqual(self.run_lab(32)[0],403)
        with connect(self.apps[32].config['DATABASE']) as db:
            roles = dict(db.execute('SELECT mode,role FROM profiles').fetchall())
        self.assertEqual(roles,{'vulnerable':'admin','secure':'user'})
        self.assertEqual(self.run_lab(32,data=LABS[31]['normal'])[0],200)

    def test_cors_requires_session_and_does_not_reflect_untrusted_origin(self):
        client = self.client(33)
        origin = 'http://127.0.0.1:5100'
        self.assertEqual(client.get('/api/secure/account').status_code,401)
        client.get('/account')
        response = client.get('/api/vulnerable/account',headers={'Origin':origin})
        self.assertEqual(response.json['account'],'alice')
        self.assertEqual(response.headers['Access-Control-Allow-Origin'],origin)
        self.assertEqual(response.headers['Access-Control-Allow-Credentials'],'true')
        response = client.get('/api/secure/account',headers={'Origin':origin})
        self.assertNotIn('Access-Control-Allow-Origin',response.headers)

    def test_real_concurrent_withdrawals_preserve_secure_balance(self):
        _, vulnerable = self.run_lab(34,'vulnerable',{'amount':'80'})
        self.assertIn('Saldo akhir: -60',vulnerable['detail'])
        _, secure = self.run_lab(34,'secure',{'amount':'80'})
        self.assertIn('Saldo akhir: 20',secure['detail'])
        self.assertEqual(sum(row['penarikan']=='diterima' for row in secure['rows']),1)
        _, normal = self.run_lab(34,'secure',{'amount':'40'})
        self.assertEqual(sum(row['penarikan']=='diterima' for row in normal['rows']),2)

    def test_idempotency_survives_requests_and_rejects_changed_amount(self):
        data = {'request_id':'invoice-123','amount':'30','repeats':'3'}
        self.run_lab(35,'vulnerable',data)
        self.run_lab(35,'secure',data)
        self.run_lab(35,'secure',data)
        self.assertEqual(self.run_lab(35,'secure',{**data,'amount':'31'})[0],409)
        with connect(self.apps[35].config['DATABASE']) as db:
            counts = dict(db.execute('SELECT mode,COUNT(*) FROM payments GROUP BY mode').fetchall())
        self.assertEqual(counts,{'vulnerable':3,'secure':1})

    def concurrent_requests(self, number, payload, workers=2):
        self.client(number)
        app, lab = self.apps[number], LABS[number-1]
        barrier = threading.Barrier(workers, timeout=10)
        def worker(index):
            client = app.test_client()
            html = client.get('/',base_url=lab['url']).text
            token = re.search(r'name="_lab_token" value="([^"]+)"',html)[1]
            barrier.wait()
            return client.post('/run/secure',base_url=lab['url'],data={**payload,'_lab_token':token}).status_code
        with ThreadPoolExecutor(max_workers=workers) as executor:
            return list(executor.map(worker,range(workers)))

    def test_concurrent_idempotency_creates_only_one_payment(self):
        statuses = self.concurrent_requests(35,{'request_id':'same-concurrent-key','amount':'50','repeats':'1'})
        self.assertEqual(statuses,[200,200])
        with connect(self.apps[35].config['DATABASE']) as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM payments WHERE mode='secure'").fetchone()[0],1)

    def test_concurrent_login_attempts_do_not_bypass_shared_limit(self):
        statuses = self.concurrent_requests(9,{'candidates':'wrong-one\nwrong-two'},workers=3)
        self.assertEqual(sorted(statuses),[401,429,429])
        with connect(self.apps[9].config['DATABASE']) as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM attempts WHERE mode='secure' AND success=0").fetchone()[0],3)

    def test_smuggling_rejects_ambiguous_and_trailing_bytes(self):
        self.assertEqual(self.run_lab(36)[0],400)
        field = LABS[35]['fields'][0]['name']
        for raw in ('POST / HTTP/1.1\r\nHost: lab.test\r\nContent-Length: 1\r\nContent-Length: 2\r\n\r\nab',
                    'POST / HTTP/1.1\r\nHost: lab.test\r\nContent-Length: 1\r\n\r\nab'):
            self.assertEqual(self.run_lab(36,data={field:raw})[0],400)
        self.assertEqual(self.run_lab(36,data=LABS[35]['normal'])[0],200)

    def test_dns_detection_filters_approved_cdn(self):
        _, result = self.run_lab(37)
        alerts = [row['domain'] for row in result['rows'] if row['alert']]
        self.assertEqual(alerts,['telemetry.lab.test'])

    def test_threat_controls_cover_paths_backup_does_not_prevent_disclosure(self):
        _, initial = self.run_lab(38,data={'controls':'tls'})
        self.assertIn('4 jalur belum diputus',initial['detail'])
        _, backup = self.run_lab(38,data={'controls':'tls,backup'})
        self.assertEqual([row['terputus dalam model'] for row in initial['rows']], [row['terputus dalam model'] for row in backup['rows']])
        _, complete = self.run_lab(38,data=LABS[37]['normal'])
        self.assertIn('0 jalur belum diputus',complete['detail'])

    def test_artifact_hash_from_untrusted_source_is_not_enough(self):
        self.assertEqual(self.run_lab(39,'vulnerable')[0],200)
        self.assertEqual(self.run_lab(39,'secure')[0],403)
        self.assertEqual(self.run_lab(39,data=LABS[38]['normal'])[0],200)

    def test_reset_restores_new_tables_without_affecting_other_lab(self):
        self.run_lab(32,'vulnerable')
        self.run_lab(35,'vulnerable')
        client = self.client(32)
        html = client.get('/').text
        token = re.search(r'name="_lab_token" value="([^"]+)"',html)[1]
        self.assertEqual(client.post('/reset',data={'_lab_token':token}).status_code,302)
        with connect(self.apps[32].config['DATABASE']) as db:
            self.assertEqual(db.execute("SELECT role FROM profiles WHERE mode='vulnerable'").fetchone()[0],'user')
        with connect(self.apps[35].config['DATABASE']) as db:
            self.assertGreater(db.execute('SELECT COUNT(*) FROM payments').fetchone()[0],0)


if __name__ == '__main__':
    unittest.main()
