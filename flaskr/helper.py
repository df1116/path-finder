import math

from googlemaps import Client
from googlemaps.elevation import elevation
from gpxpy import parse
from gpxpy.gpx import GPXRoute, GPXRoutePoint, GPXWaypoint
from requests import exceptions, post


gmaps_client = Client(key='AIzaSyCQU82Xsko1YXK8Q8Owb3Zqk2pfSRXuSoE')


def is_valid_gpx_file(file) -> bool:
    """Check if the file is a GPX file based on its filename."""
    return file.filename.endswith('.gpx')


def parse_gpx(gpx_raw: str):
    """Parse raw GPX data into a GPX object."""
    try:
        return parse(gpx_raw)
    except Exception as e:
        return ValueError(f"Failed to parse GPX file: {e}")


def standardise_gpx(gpx):
    """Standardise incoming GPX data so that all information is held within routes."""
    for track in gpx.tracks:
        route = GPXRoute()
        gpx.routes.append(route)

        for segment in track.segments:
            for point in segment.points:
                route.points.append(GPXRoutePoint(point.latitude, point.longitude, elevation=point.elevation))

    gpx.tracks = []


def http_post(api_url: str, headers: dict, body: dict):
    """Perform an HTTP POST request and return the response object."""
    try:
        response = post(api_url, headers=headers, json=body)
        response.raise_for_status()
        return response
    except exceptions.RequestException as e:
        raise ConnectionError(f"API call failed: {e}")


def get_route(coordinates):
    """Gets a route between two points using OpenRouteService."""
    api_url = 'https://api.openrouteservice.org/v2/directions/foot-hiking/gpx'
    headers = {
        'Authorization': '5b3ce3597851110001cf6248488e0d1ffe854d10ba214b419ba561d0',
        'Content-Type': 'application/json'
    }
    body = {
        'coordinates': coordinates
    }
    response = http_post(api_url, headers, body)
    gpx = parse_gpx(response.text)
    get_elevation(gpx)
    return gpx


def get_elevation(gpx):
    """Gets the elevation of given points."""
    coordinates = [(point.latitude, point.longitude) for point in gpx.routes[0].points]

    elevation_data = []
    batch_size = 512
    for i in range(0, len(coordinates), batch_size):
        batch = coordinates[i:i+batch_size]
        response = elevation(gmaps_client, batch)
        elevation_data.extend(response)

    for i, point in enumerate(gpx.routes[0].points):
        point.elevation = elevation_data[i]['elevation']


def process_add_point(gpx, longitude, latitude):
    """Adds a point to a GPX instance."""
    coordinates = get_coordinates(gpx)
    # Sort out coordinates to build route
    min_change = float('inf')
    min_i = -1
    for i in range(len(coordinates) - 1):
        change = (
                math.sqrt((longitude - coordinates[i][0]) ** 2 + (latitude - coordinates[i][1]) ** 2) +
                math.sqrt((longitude - coordinates[i + 1][0]) ** 2 + (latitude - coordinates[i + 1][1]) ** 2)
        )
        if change < min_change:
            min_i = i
            min_change = change

    coordinates.insert(min_i + 1, [longitude, latitude])

    # Sort out waypoints
    gpx.waypoints.insert(min_i, GPXWaypoint(longitude=longitude,    latitude=latitude))

    route_gpx = get_route(coordinates)
    gpx.routes[0] = route_gpx.routes[0]


def process_append_point(gpx, longitude, latitude):
    """Appends a point to a GPX instance."""
    coordinates = get_coordinates(gpx)
    # Sort out coordinates to build route
    coordinates.append([longitude, latitude])

    # Sort out waypoints
    gpx.waypoints.append(GPXWaypoint(longitude=gpx.routes[0].points[-1].longitude,
                                     latitude=gpx.routes[0].points[-1].latitude))

    route_gpx = get_route(coordinates)
    gpx.routes[0] = route_gpx.routes[0]


def process_move_point(gpx, longitude, latitude, new_longitude, new_latitude):
    """Moves a point in a GPX instance."""
    coordinates = get_coordinates(gpx)

    i_match = find_matching_point_index(coordinates, longitude, latitude)
    if i_match:
        # Sort out coordinates to build route
        coordinates[i_match] = [new_longitude, new_latitude]

        # Sort out waypoints
        if 0 < i_match < len(coordinates) - 1:
            gpx.waypoints[i_match - 1] = GPXWaypoint(longitude=new_longitude, latitude=new_latitude)

    route_gpx = get_route(coordinates)
    gpx.routes[0] = route_gpx.routes[0]


def process_remove_point(gpx, longitude, latitude):
    """Removes a point from a GPX instance."""
    coordinates = get_coordinates(gpx)
    i_match = find_matching_point_index(coordinates, longitude, latitude)

    if i_match is not None:
        # Sort out coordinates to build route
        coordinates.pop(i_match)

        # Sort out waypoints
        if 0 < i_match < len(coordinates):
            gpx.waypoints.pop(i_match - 1)
        else:
            gpx.waypoints.pop(0)

    route_gpx = get_route(coordinates)
    gpx.routes[0] = route_gpx.routes[0]


def get_coordinates(gpx):
    """Extracts the coordinates from a GPX instance."""
    coordinates = [[gpx.routes[0].points[0].longitude, gpx.routes[0].points[0].latitude]]

    for waypoint in gpx.waypoints:
        coordinates.append([waypoint.longitude, waypoint.latitude])

    coordinates.append([gpx.routes[0].points[-1].longitude, gpx.routes[0].points[-1].latitude])

    return coordinates


def find_matching_point_index(coordinates, longitude, latitude):
    """Finds the index of a point matching the given longitude and latitude."""
    for i, (lon, lat) in enumerate(coordinates):
        if points_match(lon, longitude, lat, latitude):
            return i
    return None


def points_match(long1, long2, lat1, lat2):
    """Check if two geographical points are approximately equal."""
    return abs(long1 - long2) <= 0.00001 and abs(lat1 - lat2) <= 0.00001
