import os
os.environ['DEMO_ONLY']='true'
from starlette.testclient import TestClient
from server import app
import pytest

@pytest.fixture(scope='module')
def client():
    with TestClient(app) as c:
        yield c

def test_health_sample_and_no_persistence(client):
    c=client
    assert c.get('/health').json()['mode']=='synthetic-demo'
    a=c.get('/api/demo');b=c.get('/api/demo')
    assert a.status_code==200 and a.json()==b.json()
    assert a.headers['cache-control']=='no-store'
    assert c.get('/').status_code==200
    assert c.get('/samples/invoices.csv').text.startswith('id,tenant')
    assert c.get('/samples/nope.csv').status_code==404

def test_hosted_demo_refuses_private_uploads(client):
    assert client.post('/api/reconcile',json={'invoices_csv':'sensitive'}).status_code==403

def test_mcp_rejects_bad_host(client):
    r=client.post('/mcp',headers={'host':'attacker.invalid','content-type':'application/json'},json={})
    assert r.status_code==421


def test_public_widget_has_resolved_mode_and_security_policy(client):
    r=client.get('/')
    assert 'const demoOnly=true;' in r.text
    assert '__DEMO_ONLY__' not in r.text
    assert "base-uri 'none'" in r.headers['content-security-policy']
    assert r.headers['x-content-type-options']=='nosniff'
