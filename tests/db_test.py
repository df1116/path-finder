import sqlalchemy.orm

from flaskr.db import create_engine


db_engine = create_engine('sqlite:///:memory:')
db_session = sqlalchemy.orm.scoped_session(sqlalchemy.orm.sessionmaker(autocommit=False,
                                                                       autoflush=False,
                                                                       bind=db_engine))


def test_engine_connection():
    """Test the database engine connection."""
    try:
        conn = db_engine.connect()
        assert conn
    finally:
        conn.close()
