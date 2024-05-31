import json

from gpxpy import parse
from gpxpy.gpx import GPXRoute, GPXRoutePoint, GPXWaypoint
from requests import exceptions, post

from flaskr.api_keys import (
    openrouteservice_api_key)


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


def http_post(api_url: str, api_key: str, body: dict):
    """Perform an HTTP POST request and return the response object."""
    try:
        headers = {
            'Authorization': api_key,
            'Content-Type': 'application/json'
        }
        response = post(api_url, headers=headers, json=body)
        response.raise_for_status()
        return response
    except exceptions.RequestException as e:
        raise ConnectionError(f"API call failed: {e}")


def get_route(coordinates, profile):
    """Gets a route between two points using OpenRouteService."""
    api_url = f'https://api.openrouteservice.org/v2/directions/{profile}/gpx'
    body = {
        'coordinates': coordinates,
        'elevation': True
    }
    response = http_post(api_url, openrouteservice_api_key, body)
    gpx = parse_gpx(response.text)
    return gpx


def get_distances(locations, profile):
    """Gets a route between two points using OpenRouteService."""
    api_url = f'https://api.openrouteservice.org/v2/matrix/{profile}'
    body = {
        'locations': locations,
        'destinations': [len(locations) - 1],
        'metrics': ['distance']
    }
    response = http_post(api_url, openrouteservice_api_key, body)
    return json.loads(response.text)['distances'][:-1]


def process_set_start(gpx, _, longitude, latitude):
    """Sets the start of a GPX instance."""
    gpx.routes.append(GPXRoute())
    gpx.routes[0].points.append(GPXWaypoint(longitude=longitude, latitude=latitude))


def process_set_end(gpx, profile, longitude, latitude):
    """Sets the end of a GPX instance."""
    coordinates = [[gpx.routes[0].points[0].longitude, gpx.routes[0].points[0].latitude], [longitude, latitude]]
    route_gpx = get_route(coordinates, profile)
    gpx.routes[0] = route_gpx.routes[0]


def process_add_point(gpx, profile, longitude, latitude):
    """Adds a point to a GPX instance."""
    coordinates = get_coordinates(gpx)
    locations = coordinates + [[longitude, latitude]]
    distances = get_distances(locations, profile)
    # Sort out coordinates to build route
    min_change = float('inf')
    min_i = -1
    for i in range(len(distances) - 1):
        change = distances[i][0] + distances[i + 1][0]
        if change < min_change:
            min_i = i
            min_change = change

    coordinates.insert(min_i + 1, [longitude, latitude])

    # Sort out waypoints
    gpx.waypoints.insert(min_i, GPXWaypoint(longitude=longitude, latitude=latitude))

    route_gpx = get_route(coordinates, profile)
    gpx.routes[0] = route_gpx.routes[0]


def process_append_point(gpx, profile, longitude, latitude):
    """Appends a point to a GPX instance."""
    coordinates = get_coordinates(gpx)
    # Sort out coordinates to build route
    coordinates.append([longitude, latitude])

    # Sort out waypoints
    gpx.waypoints.append(GPXWaypoint(longitude=gpx.routes[0].points[-1].longitude,
                                     latitude=gpx.routes[0].points[-1].latitude))

    route_gpx = get_route(coordinates, profile)
    gpx.routes[0] = route_gpx.routes[0]


def process_move_point(gpx, profile, longitude, latitude, new_longitude, new_latitude):
    """Moves a point in a GPX instance."""
    coordinates = get_coordinates(gpx)

    i_match = find_matching_point_index(coordinates, longitude, latitude)
    if i_match:
        # Sort out coordinates to build route
        coordinates[i_match] = [new_longitude, new_latitude]

        # Sort out waypoints
        if 0 < i_match < len(coordinates) - 1:
            gpx.waypoints[i_match - 1] = GPXWaypoint(longitude=new_longitude, latitude=new_latitude)

    route_gpx = get_route(coordinates, profile)
    gpx.routes[0] = route_gpx.routes[0]


def process_remove_point(gpx, profile, longitude, latitude):
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

    route_gpx = get_route(coordinates, profile)
    gpx.routes[0] = route_gpx.routes[0]


def process_update_profile(gpx, profile):
    """Updates the profile of a GPX instance."""
    coordinates = get_coordinates(gpx)

    route_gpx = get_route(coordinates, profile)
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
