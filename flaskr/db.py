import sqlalchemy.orm

engine = sqlalchemy.create_engine('sqlite:///test.db')
db_session = sqlalchemy.orm.scoped_session(sqlalchemy.orm.sessionmaker(autocommit=False,
                                                                       autoflush=False,
                                                                       bind=engine))
Base = sqlalchemy.orm.declarative_base()
Base.query = db_session.query_property()


def init_db():
    Base.metadata.create_all(bind=engine)