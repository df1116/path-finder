from sqlalchemy import create_engine as sqlalchemy_create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session


Base = declarative_base()


def create_engine(db_url):
    return sqlalchemy_create_engine(db_url)


engine = create_engine('sqlite:///test.db')


def create_db_session(e):
    session_factory = sessionmaker(bind=e, autocommit=False, autoflush=False)
    return scoped_session(session_factory)


db_session = create_db_session(engine)
Base.query = db_session.query_property()


def init_db():
    Base.metadata.create_all(bind=engine)


def db_add(to_add):
    db_session.add(to_add)


def db_delete(to_delete):
    db_session.delete(to_delete)


def db_commit():
    try:
        db_session.commit()
    except SQLAlchemyError as e:
        db_session.rollback()
        print(f"An error occurred: {e}")
    finally:
        shutdown_session()


def shutdown_session(exception=None):
    db_session.remove()
