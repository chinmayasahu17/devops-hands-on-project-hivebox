import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_version(client):
    rv = client.get('/version')
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert 'version' in json_data
    assert json_data['version'] == '0.0.1'

def test_temperature(client):
    rv = client.get('/temperature')
    assert rv.status_code == 200
    json_data = rv.get_json()
    # average_temperature can be None if no data, so check key presence
    assert 'average_temperature' in json_data
