from sqlalchemy import Any, BLOB, Column, Integer, String

from flaskr.db import Base


class Gpx(Base):
    """
    Represents a GPX file entity storing GPS data.
    """
    __tablename__ = 'gpx'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    profile = Column(String(255))
    data = Column(BLOB)

    def __repr__(self):
        """
        Return a formal string representation of the GPX object.
        """
        return f"<Gpx(name={self.name!r}, id={self.id})>"
