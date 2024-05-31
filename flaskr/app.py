from flask import Flask, render_template, Response, request, redirect, url_for

from flaskr.helper import (parse_gpx, process_add_point, process_append_point, process_move_point, process_set_start,
                           process_set_end, process_remove_point, process_update_profile)
from flaskr.service import (create_gpx_file, upload_gpx_file, get_gpx_file, get_all_gpx_files, update_gpx_file,
                            delete_gpx_file)
from flaskr.db import init_db, shutdown_session


app = Flask(__name__)
init_db()


@app.route('/')
def home():
    """Home page to list all GPX files."""
    all_gpx_files = get_all_gpx_files()
    return render_template('home.html', gpx_files=all_gpx_files)


@app.route('/create_gpx', methods=['POST'])
def create_gpx():
    """Upload a GPX file and save it."""
    name = request.form.get('name')
    profile = request.form.get('profile')
    create_gpx_file(name, profile)
    return render_template('view_gpx.html', filename=f'{name}.gpx', profile=profile)


@app.route('/upload', methods=['POST'])
def upload_gpx():
    """Upload a GPX file and save it."""
    profile = request.form.get('profile')
    file = request.files.get('file')
    if file and file.filename.endswith('.gpx'):
        upload_gpx_file(profile, file)
        return redirect(url_for('home'))
    return 'Invalid file', 400


@app.route('/view/<filename>/<profile>')
def view_gpx(filename, profile):
    """Display a specific GPX file."""
    return render_template('view_gpx.html', filename=filename, profile=profile)


def handle_point_action(filename, process_function):
    """Handle actions related to GPX points."""
    longitude = float(request.form["longitude"])
    latitude = float(request.form["latitude"])

    gpx_file = get_gpx_file(filename)
    profile = gpx_file.profile
    gpx = parse_gpx(gpx_file.data)

    process_function(gpx, gpx_file.profile, longitude, latitude)

    update_gpx_file(gpx_file, gpx)

    return redirect(url_for('view_gpx', filename=filename, profile=profile))


@app.route('/set_start/<filename>', methods=['POST'])
def set_start(filename):
    """Set the start of a GPX file."""
    return handle_point_action(filename, process_set_start)


@app.route('/set_end/<filename>', methods=['POST'])
def set_end(filename):
    """Set the end of a GPX file."""
    return handle_point_action(filename, process_set_end)


@app.route('/add_point/<filename>', methods=['POST'])
def add_point(filename):
    """Add a point to a GPX file and save it."""
    return handle_point_action(filename, process_add_point)


@app.route('/append_point/<filename>', methods=['POST'])
def append_point(filename):
    """Append a point to a GPX file and save it."""
    return handle_point_action(filename, process_append_point)


@app.route('/move_point/<filename>', methods=['POST'])
def move_point(filename):
    """Add a point to a GPX file and save it."""
    longitude = float(request.form["longitude"])
    latitude = float(request.form["latitude"])
    new_longitude = float(request.form["new_longitude"])
    new_latitude = float(request.form["new_latitude"])

    gpx_file = get_gpx_file(filename)
    profile = gpx_file.profile
    gpx = parse_gpx(gpx_file.data)

    process_move_point(gpx, gpx_file.profile, longitude, latitude, new_longitude, new_latitude)

    update_gpx_file(gpx_file, gpx)

    return redirect(url_for('view_gpx', filename=filename, profile=profile))


@app.route('/remove_point/<filename>', methods=['POST'])
def remove_point(filename):
    """Remove a point from a GPX file and save it."""
    return handle_point_action(filename, process_remove_point)


@app.route('/delete/<filename>')
def delete_gpx(filename):
    """Delete a GPX file."""
    delete_gpx_file(filename)
    return redirect(url_for('home'))


@app.route('/update_profile/<filename>', methods=['POST'])
def update_profile(filename):
    """Update the profile of a gpx route."""
    profile = request.form.get('profile')

    gpx_file = get_gpx_file(filename)
    gpx = parse_gpx(gpx_file.data)

    process_update_profile(gpx, profile)

    update_gpx_file(gpx_file, new_gpx=gpx, new_profile=profile)

    return redirect(url_for('view_gpx', filename=filename, profile=profile))


@app.route('/downloads/<filename>')
def download_gpx(filename):
    """Download a GPX file."""
    gpx = get_gpx_file(filename)
    return Response(
        gpx.data,
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Type": "application/octet-stream"
        }
    )


@app.teardown_appcontext
def teardown(exception=None):
    """Remove database session at the end of the request or when app shuts down."""
    shutdown_session()


if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'], port=5000)
