from flaskr.db import db_session
from flaskr.models import Gpx


def upload_gpx_file(file):
    """Upload a new GPX file to the database."""
    filename = file.filename
    data = file.read()
    if not filename.endswith('.gpx'):
        raise ValueError("Unsupported file format")
    gpx = Gpx(name=filename, data=data)
    db_session.add(gpx)
    db_session.commit()


def get_gpx_file(filename):
    """Retrieve a GPX file by its name from the database."""
    return Gpx.query.filter_by(name=filename).first()


def get_all_gpx_files():
    """Retrieve all GPX files stored in the database."""
    return Gpx.query.all()


def update_gpx_file(gpx_file, new_gpx):
    """Update a GPX file in the database with new data."""
    gpx_file.data = new_gpx.to_xml().encode('utf-8')
    db_session.commit()


def delete_gpx_file(filename):
    """Delete a GPX file from the database by its filename."""
    gpx = get_gpx_file(filename)
    if not gpx:
        raise FileNotFoundError("File not found")
    db_session.delete(gpx)
    db_session.commit()
