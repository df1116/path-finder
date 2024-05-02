import requests
import flask
import gpxpy

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
    """Add a point to an existing GPX file and route it along real roads or paths."""
    gpx_file = service.get_gpx_file(filename)
    try:
        gpx = gpxpy.parse(gpx_file.data)
    except Exception as e:
        app.logger.error(f"Error parsing GPX data: {str(e)}")
        return 'Failed to parse GPX file', 400

    try:
        longitude = float(flask.request.form["longitude"])
        latitude = float(flask.request.form["latitude"])
    except ValueError:
        return 'Invalid latitude or longitude', 400

    # Using the OpenRouteService API to get the route
    api_url = 'https://api.openrouteservice.org/v2/directions/foot-hiking/gpx'
    headers = {
        'Authorization': '5b3ce3597851110001cf6248488e0d1ffe854d10ba214b419ba561d0',
        'Content-Type': 'application/json'
    }
    end_point = gpx.tracks[0].segments[0].points[-1]
    body = {
        'coordinates': [
            [end_point.longitude, end_point.latitude],
            [longitude, latitude]
        ]
    }

    try:
        response = requests.post(api_url, headers=headers, json=body)
        response.raise_for_status()
        route_gpx = gpxpy.parse(response.text)
        gpx.routes.append(route_gpx.routes[0])
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Failed to get route from API: {str(e)}")
        return f"API call failed: {str(e)}", 500

    gpx_file.data = gpx.to_xml().encode('utf-8')
    db.db_session.commit()

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
    app.run(debug=app.config['DEBUG'], port=app.config['PORT'])
