import pytest
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from db import Base


@pytest.fixture(scope="module")
def test_engine():
    """Create an in-memory SQLite engine for testing."""
    return create_engine('sqlite:///:memory:')


@pytest.fixture(scope="module")
def db_session(test_engine):
    """Provides a transactional scope around a series of operations."""
    session_factory = sessionmaker(bind=test_engine)
    session = scoped_session(session_factory)
    yield session
    session.remove()


def test_engine_connection(test_engine):
    """Test the database engine connection."""
    try:
        conn = test_engine.connect()
        assert conn
    finally:
        conn.close()


def test_init_db(test_engine):
    """Test initializing the database schema."""
    Base.metadata.create_all(test_engine)  # Explicitly bind to test_engine
    inspector = sqlalchemy.inspect(test_engine)
    assert inspector.get_table_names() == []  # Adjust expected table names as per your schema


@pytest.mark.usefixtures("db_session")
def test_db_operations(db_session):
    """Placeholder test to demonstrate how you might test actual db operations."""
    # Example of adding a new object to the session and committing it
    # Assuming a model `MyModel` exists
    # new_obj = MyModel(name="test")
    # db_session.add(new_obj)
    # db_session.commit()
    # assert new_obj.id is not None  # assuming `id` is auto-generated
    pass
