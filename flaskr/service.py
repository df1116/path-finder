from flaskr.db import db_add, db_commit, db_delete
from flaskr.helper import is_valid_gpx_file, parse_gpx, standardise_gpx
from flaskr.models import Gpx


def upload_gpx_file(profile, file):
    """Upload a new GPX file to the database."""
    if not is_valid_gpx_file(file):
        raise ValueError("Unsupported file format")

    filename = file.filename
    data = file.read()

    gpx = parse_gpx(data)
    standardise_gpx(gpx)

    gpx_to_add = Gpx(name=filename, profile=profile, data=gpx.to_xml().encode('utf-8'))

    db_add(gpx_to_add)
    db_commit()


def get_gpx_file(filename):
    """Retrieve a GPX file by its name from the database."""
    gpx_file = Gpx.query.filter_by(name=filename).first()
    if not gpx_file:
        raise FileNotFoundError(f"GPX file '{filename}' not found")
    return gpx_file


def get_all_gpx_files():
    """Retrieve all GPX files stored in the database."""
    return Gpx.query.all()


def update_gpx_file(gpx_file, new_gpx=None, new_profile=None):
    """Update a GPX file in the database with new data."""
    if new_profile:
        gpx_file.profile = new_profile
    if new_gpx:
        gpx_file.data = new_gpx.to_xml().encode('utf-8')
    db_commit()


def delete_gpx_file(filename):
    """Delete a GPX file from the database by its filename."""
    gpx = get_gpx_file(filename)
    db_delete(gpx)
    db_commit()
