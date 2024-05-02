import sqlalchemy

import db


class Gpx(db.Base):
    __tablename__ = 'gpx'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String, unique=False)
    data = sqlalchemy.Column(sqlalchemy.BLOB)

    def __init__(self, name=None, data=None, **kw: sqlalchemy.Any):
        super().__init__(**kw)
        self.name = name
        self.data = data

    def __repr__(self):
        return f'<{self.name!r}>'
