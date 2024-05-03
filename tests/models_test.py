import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from db import Base
from models import Gpx


@pytest.fixture(scope="module")
def db_session():
    """Create a session for testing, separate from the main database."""
    engine = create_engine('sqlite:///:memory:')  # Using an in-memory database for tests
    Base.metadata.create_all(engine)  # Create all tables based on Base metadata
    session_factory = sessionmaker(bind=engine)
    session = scoped_session(session_factory)
    yield session()
    session.remove()
    Base.metadata.drop_all(engine)


def test_create_gpx(db_session):
    """Test creating a Gpx instance and saving it to the database."""
    gpx_instance = Gpx(name="test.gpx", data=b"GPX data")
    db_session.add(gpx_instance)
    db_session.commit()

    assert gpx_instance.id is not None  # Primary key should be set automatically
    assert gpx_instance.name == "test.gpx"
    assert gpx_instance.data == b"GPX data"


def test_repr_method(db_session):
    """Test the __repr__ method for a Gpx instance."""
    gpx_instance = Gpx(name="repr_test.gpx")
    db_session.add(gpx_instance)
    db_session.commit()

    assert repr(gpx_instance) == "<'repr_test.gpx'>"
