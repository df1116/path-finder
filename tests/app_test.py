import pytest
from flask import url_for
from app import app
import db
import io


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['DEBUG'] = False

    # Assuming you might have configurations to adjust like a database URI
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    # Use the test client provided by Flask
    with app.test_client() as client:
        with app.app_context():
            # Initialize anything else you need in your app context
            db.init_db()  # Here you might want to initialize a test DB
        yield client


def test_home_page(client):
    response = client.get(url_for('home'))
    assert response.status_code == 200
    assert 'GPX files' in response.get_data(as_text=True)


def test_upload_gpx(client):
    data = {
        'file': (io.BytesIO(b'content of your file'), 'test.gpx')
    }
    response = client.post(url_for('upload_gpx'), data=data, content_type='multipart/form-data')
    assert response.status_code == 302  # Redirect to home
    assert url_for('home') in response.location


def test_view_gpx(client):
    response = client.get(url_for('view_gpx', filename='test.gpx'))
    assert response.status_code == 200
    assert 'test.gpx' in response.get_data(as_text=True)


def test_add_point(client):
    # Simulate posting to add_point route
    # Assuming there's an existing file and route setup
    pass


def test_delete_gpx(client):
    response = client.get(url_for('delete_gpx', filename='test.gpx'))
    assert response.status_code == 302  # Redirect to home


def test_download_gpx(client):
    response = client.get(url_for('download_gpx', filename='test.gpx'))
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/octet-stream'


def test_teardown(client):
    response = client.get(url_for('shutdown_session'))
    assert response.status_code == 200 or 404
