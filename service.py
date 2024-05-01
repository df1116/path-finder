from db import db_session
from models import Gpx


def get_gpx_file(filename):
    return Gpx.query.filter(Gpx.name == filename).first()


def get_all_gpx_files():
    return Gpx.query.all()


def upload_gpx_file(file):
    filename = file.filename
    data = file.read()
    gpx = Gpx(name=filename, data=data)
    db_session.add(gpx)
    db_session.commit()


def delete_gpx_file(filename):
    gpx = get_gpx_file(filename)
    db_session.delete(gpx)
    db_session.commit()
