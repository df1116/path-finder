from pytest import fixture

from flaskr.db import Base, create_engine, create_db_session
from flaskr.models import Gpx


@fixture(scope="module")
def db_session():
    """Create a session for testing, separate from the main database."""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    session = create_db_session(engine)
    Base.query = session.query_property()
    yield session()
    session.remove()
    Base.metadata.drop_all(engine)


def test_create_gpx(db_session):
    """Test creating a Gpx instance and saving it to the database."""
    gpx_instance = Gpx(name="test1.gpx", data=b"GPX data")
    db_session.add(gpx_instance)
    db_session.commit()

    assert gpx_instance.id is not None
    assert gpx_instance.name == "test1.gpx"
    assert gpx_instance.data == b"GPX data"


def test_repr_method(db_session):
    """Test the __repr__ method for a Gpx instance."""
    gpx_instance = Gpx(name="test2.gpx", data=b"GPX data")
    db_session.add(gpx_instance)
    db_session.commit()

    assert repr(gpx_instance).startswith("<Gpx(name='test2.gpx', id=")
