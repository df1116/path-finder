import flask

import helper
import service
import db

app = flask.Flask(__name__)

db.init_db()


@app.route('/')
def home():
    """Home page to list all GPX files."""
    all_gpx_files = service.get_all_gpx_files()
    return flask.render_template('home.html', gpx_files=all_gpx_files)


@app.route('/upload', methods=['POST'])
def upload_gpx():
    """Upload a GPX file and save it."""
    file = flask.request.files.get('file')
    if file and file.filename.endswith('.gpx'):
        service.upload_gpx_file(file)
        return flask.redirect(flask.url_for('home'))
    return 'Invalid file', 400


@app.route('/view/<filename>')
def view_gpx(filename):
    """Display a specific GPX file."""
    return flask.render_template('view_gpx.html', filename=filename)


@app.route('/add_point/<filename>', methods=['POST'])
def add_point(filename):
    longitude = float(flask.request.form["longitude"])
    latitude = float(flask.request.form["latitude"])

    gpx_file = service.get_gpx_file(filename)
    gpx = helper.parse_gpx(gpx_file.data)

    if len(gpx.routes) > 0:
        start_point = gpx.routes[-1].points[-1]
    else:
        start_point = gpx.tracks[0].segments[0].points[-1]

    route_gpx = helper.get_route(start_point.longitude, start_point.latitude, longitude, latitude)

    gpx.routes.append(route_gpx.routes[0])
    service.update_gpx_file(gpx_file, gpx)

    return flask.redirect(flask.url_for('view_gpx', filename=filename))


@app.route('/remove_point/<filename>', methods=['POST'])
def remove_point(filename):
    longitude = float(flask.request.form["longitude"])
    latitude = float(flask.request.form["latitude"])

    gpx_file = service.get_gpx_file(filename)
    gpx = helper.parse_gpx(gpx_file.data)

    modified_gpx = helper.process_point_removal(gpx, longitude, latitude)

    service.update_gpx_file(gpx_file, modified_gpx)

    return flask.redirect(flask.url_for('view_gpx', filename=filename))


@app.route('/delete/<filename>')
def delete_gpx(filename):
    """Delete a GPX file."""
    service.delete_gpx_file(filename)
    return flask.redirect(flask.url_for('home'))


@app.route('/downloads/<filename>')
def download_gpx(filename):
    """Download a GPX file."""
    gpx = service.get_gpx_file(filename)
    return flask.Response(
        gpx.data,
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Type": "application/octet-stream"
        }
    )


@app.teardown_appcontext
def shutdown_session(exception=None):
    """Remove database session at the end of the request or when app shuts down."""
    db.db_session.remove()


if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'], port=5000)
