# Path Finder

## Overview

This GPX File Management System is a Flask-based web application designed to upload, display, and manage GPX files. Users can upload GPX files, view them on a map, add or remove points, and download or delete the files.

## Structure

The application consists of the following Python and HTML files:

### Python Files

- `app.py`: The main Flask application file with routes for uploading, viewing, adding points to, and deleting GPX files.
- `service.py`: Contains business logic for handling the database operations related to GPX files.
- `helper.py`: Provides utility functions for parsing GPX files and making HTTP requests to external services.
- `models.py`: Defines the SQLAlchemy ORM models for GPX data.
- `db.py`: Manages database connections and session configurations.

### HTML Files

- `home.html`: The homepage of the application that lists all uploaded GPX files and includes an upload form.
- `view_gpx.html`: Displays detailed information and a map view of a specific GPX file.

## Setup

### Prerequisites

Ensure you have Python installed on your machine. The application has been tested with Python 3.8. Additionally, you will need pip to install the required packages.

### Installing Dependencies

1. Clone the repository to your local machine:
2. Navigate to the cloned directory:
3. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

To run the application, use the following command:
```bash
python -m flaskr.app
```

The application will start running on `http://localhost:5000`. Navigate to this URL in your web browser to start using the GPX File Management System.

## Features

- **Upload GPX Files**: Users can upload files via the home page.
- **View GPX Files**: Click on a file in the list to view its details and location on a map.
- **Add Points to GPX Files**: While viewing a file, users can add points by submitting latitude and longitude through the provided form or by clicking on the map.
- **Remove Points from GPX Files**: Points can be removed from the map interface.
- **Download and Delete GPX Files**: Users can download or delete files from the homepage list.