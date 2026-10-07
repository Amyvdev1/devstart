from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)
def test_session_flow():
    sid=client.post('/api/sessions').json()['session_id']
    r=client.post('/api/scenarios/missing-product-id/attempt',json={'session_id':sid,'body':{'product_id':'sku_1'}})
    assert r.status_code==200 and r.json()['result']['success'] is True
    assert client.get('/api/sessions/'+sid).json()['benchmark']['completed']==1
