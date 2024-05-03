import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from db import Base
import models
import service


# Define a fixture for the database engine
@pytest.fixture(scope='module')
def engine():
    return create_engine('sqlite:///:memory:')


# Define a fixture for the database session
@pytest.fixture(scope='module')
def session(engine):
    Base.metadata.create_all(engine)
    _session = scoped_session(sessionmaker(bind=engine))
    yield _session
    _session.remove()
    Base.metadata.drop_all(engine)


# Factory to create GPX model instances
class GpxFactory:
    class Meta:
        model = models.Gpx

    name = "test.gpx"
    data = b"<gpx></gpx>"


@pytest.fixture
def gpx_file(session):
    gpx = GpxFactory()
    session.add(gpx)
    session.commit()
    return gpx


def test_upload_gpx_file(session, gpx_file):
    with open('test.gpx', 'wb') as f:
        f.write(b"<gpx></gpx>")

    with open('test.gpx', 'rb') as f:
        service.upload_gpx_file(f)

    uploaded_gpx = session.query(models.Gpx).filter_by(name='test.gpx').first()
    assert uploaded_gpx is not None
    assert uploaded_gpx.data == b"<gpx></gpx>"


def test_get_gpx_file(session, gpx_file):
    retrieved_gpx = service.get_gpx_file(gpx_file.name)
    assert retrieved_gpx == gpx_file


def test_get_all_gpx_files(session, gpx_file):
    gpx_files = service.get_all_gpx_files()
    assert len(gpx_files) == 1
    assert gpx_files[0] == gpx_file


def test_update_gpx_file(session, gpx_file):
    # Assume new_gpx is an instance of a GPX model with a to_xml() method
    new_gpx = GpxFactory(data=b"<gpx><new></new></gpx>")
    service.update_gpx_file(gpx_file, new_gpx)
    updated_gpx = session.query(models.Gpx).filter_by(name=gpx_file.name).first()
    assert updated_gpx.data == b"<gpx><new></new></gpx>"


def test_delete_gpx_file(session, gpx_file):
    service.delete_gpx_file(gpx_file.name)
    assert session.query(models.Gpx).filter_by(name=gpx_file.name).first() is None
