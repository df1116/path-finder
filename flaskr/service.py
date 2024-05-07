from flaskr.db import db_add, db_commit, db_delete
from flaskr.helper import is_valid_gpx_file
from flaskr.models import Gpx


def upload_gpx_file(file):
    """Upload a new GPX file to the database."""
    if not is_valid_gpx_file(file):
        raise ValueError("Unsupported file format")

    filename = file.filename
    data = file.read()
    gpx = Gpx(name=filename, data=data)

    db_add(gpx)
    db_commit()


def get_gpx_file(filename):
    """Retrieve a GPX file by its name from the database."""
    return Gpx.query.filter_by(name=filename).first()


def get_all_gpx_files():
    """Retrieve all GPX files stored in the database."""
    return Gpx.query.all()


def update_gpx_file(gpx_file, new_gpx):
    """Update a GPX file in the database with new data."""
    gpx_file.data = new_gpx.to_xml().encode('utf-8')
    db_commit()


def delete_gpx_file(filename):
    """Delete a GPX file from the database by its filename."""
    gpx = get_gpx_file(filename)
    if not gpx:
        raise FileNotFoundError("File not found")
    db_delete(gpx)
    db_commit()
