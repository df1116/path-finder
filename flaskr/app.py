from flask import Flask, render_template, Response, request, redirect, url_for

from flaskr.helper import parse_gpx, get_route, process_point_removal
from flaskr.service import upload_gpx_file, get_gpx_file, get_all_gpx_files, update_gpx_file, delete_gpx_file
from flaskr.db import init_db, shutdown_session


app = Flask(__name__)
init_db()


@app.route('/')
def home():
    """Home page to list all GPX files."""
    all_gpx_files = get_all_gpx_files()
    return render_template('home.html', gpx_files=all_gpx_files)


@app.route('/upload', methods=['POST'])
def upload_gpx():
    """Upload a GPX file and save it."""
    file = request.files.get('file')
    if file and file.filename.endswith('.gpx'):
        upload_gpx_file(file)
        return redirect(url_for('home'))
    return 'Invalid file', 400


@app.route('/view/<filename>')
def view_gpx(filename):
    """Display a specific GPX file."""
    return render_template('view_gpx.html', filename=filename)


@app.route('/add_point/<filename>', methods=['POST'])
def add_point(filename):
    """Add a point to a GPX file and save it."""
    longitude = float(request.form["longitude"])
    latitude = float(request.form["latitude"])

    gpx_file = get_gpx_file(filename)
    gpx = parse_gpx(gpx_file.data)

    if len(gpx.routes) > 0:
        start_point = gpx.routes[-1].points[-1]
    else:
        start_point = gpx.tracks[0].segments[0].points[-1]

    route_gpx = get_route(start_point.longitude, start_point.latitude, longitude, latitude)

    gpx.routes.append(route_gpx.routes[0])
    update_gpx_file(gpx_file, gpx)

    return redirect(url_for('view_gpx', filename=filename))


@app.route('/remove_point/<filename>', methods=['POST'])
def remove_point(filename):
    """Remove a point to a GPX file and save it."""
    longitude = float(request.form["longitude"])
    latitude = float(request.form["latitude"])

    gpx_file = get_gpx_file(filename)
    gpx = parse_gpx(gpx_file.data)

    modified_gpx = process_point_removal(gpx, longitude, latitude)

    update_gpx_file(gpx_file, modified_gpx)

    return redirect(url_for('view_gpx', filename=filename))


@app.route('/delete/<filename>')
def delete_gpx(filename):
    """Delete a GPX file."""
    delete_gpx_file(filename)
    return redirect(url_for('home'))


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
