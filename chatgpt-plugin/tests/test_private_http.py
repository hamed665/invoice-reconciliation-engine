import os,subprocess,sys,time
from pathlib import Path
import httpx,pytest
from reconciliation import sample_inputs

@pytest.fixture(scope='module')
def private_client():
    env={**os.environ,'DEMO_ONLY':'false','PORT':'8788','PUBLIC_HOST':''}
    p=subprocess.Popen([sys.executable,'server.py'],cwd=Path(__file__).parents[1],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    with httpx.Client(base_url='http://127.0.0.1:8788',trust_env=False) as c:
        try:
            for _ in range(100):
                try:
                    if c.get('/health').status_code==200:break
                except httpx.ConnectError:time.sleep(.05)
            else:raise RuntimeError('Private server not ready')
            yield c
        finally:p.terminate();p.wait(timeout=5)

def test_custom_csv_runs_real_engine(private_client):
    r=private_client.post('/api/reconcile',json=sample_inputs())
    assert r.status_code==200
    assert r.json()['summary']['matched']==1
    assert private_client.get('/health').json()['mode']=='private-local'

def test_cross_origin_and_oversize_rejected(private_client):
    assert private_client.post('/api/reconcile',json=sample_inputs(),headers={'Origin':'https://attacker.invalid'}).status_code==403
    assert private_client.post('/api/reconcile',content=b'x'*300001,headers={'Content-Type':'application/json'}).status_code==413

def test_malformed_body_is_clear_error(private_client):
    assert private_client.post('/api/reconcile',content='not json',headers={'Content-Type':'application/json'}).status_code==400
    assert private_client.post('/api/reconcile',json={'bad':'field'}).status_code==400
    assert private_client.post('/api/reconcile',content='x').status_code==415
