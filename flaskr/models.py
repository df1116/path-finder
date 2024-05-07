from sqlalchemy import Any, BLOB, Column, Integer, String

from flaskr.db import Base


class Gpx(Base):
    __tablename__ = 'gpx'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=False)
    data = Column(BLOB)

    def __init__(self, name=None, data=None, **kw: Any):
        super().__init__(**kw)
        self.name = name
        self.data = data

    def __repr__(self):
        return f'<{self.name!r}>'
