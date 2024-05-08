import flask
import io
import pytest

from flaskr.app import app
from flaskr.db import init_db


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['DEBUG'] = False
    app.config['SERVER_NAME'] = 'localhost:5000'
    app.config['APPLICATION_ROOT'] = '/'
    app.config['PREFERRED_URL_SCHEME'] = 'http'

    with app.test_client() as client:
        with app.app_context():
            init_db()
            yield client


def test_home_page(client):
    response = client.get(flask.url_for('home'))
    assert response.status_code == 200
    assert 'View and Manage GPX Files' in response.get_data(as_text=True)


def test_upload_gpx(client):
    data = {
        'file': (io.BytesIO(b"GPX data"), "test.gpx")
    }
    response = client.post(flask.url_for('upload_gpx'), data=data, content_type='multipart/form-data')
    assert response.status_code == 302
    assert flask.url_for('home') in response.location


def test_view_gpx(client):
    response = client.get(flask.url_for('view_gpx', filename='test.gpx'))
    assert response.status_code == 200
    assert 'test.gpx' in response.get_data(as_text=True)


def test_delete_gpx(client):
    response = client.get(flask.url_for('delete_gpx', filename='test.gpx'))
    assert response.status_code == 302
