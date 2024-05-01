from flask import Flask, render_template, request, redirect, url_for, Response
import gpxpy

import service
from db import db_session, init_db


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'gpx_files'
init_db()


@app.route('/')
def home():
    all_gpx_files = service.get_all_gpx_files()
    return render_template('home.html', gpx_files=all_gpx_files)


@app.route('/upload', methods=['POST'])
def upload_gpx():
    file = request.files['file']
    if file and file.filename.endswith('.gpx'):
        service.upload_gpx_file(file)
        return redirect(url_for('home'))
    return 'Invalid file', 400


@app.route('/view/<filename>')
def view_gpx(filename):
    return render_template('view_gpx.html', filename=filename)


@app.route('/add_point/<filename>', methods=['POST'])
def add_point(filename):
    gpx = service.get_gpx_file(filename)
    data = gpx.data
    latitude = request.form["latitude"]
    longitude = request.form["longitude"]
    gpx = gpxpy.parse(data)
    add_point()
    return redirect(url_for('view_gpx', filename=filename))


@app.route('/delete/<filename>')
def delete_gpx(filename):
    service.delete_gpx_file(filename)
    return redirect(url_for('home'))


@app.route('/downloads/<filename>')
def download_gpx(filename):
    gpx = service.get_gpx_file(filename)
    return Response(
        gpx.data,
        headers={
            "Content-Disposition": f"attachment; filename={gpx.name}",
            "Content-Type": "application/octet-stream"
        }
    )


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


if __name__ == '__main__':
    app.run(debug=True, port=5000)
