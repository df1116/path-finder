import requests

import gpxpy


def parse_gpx(gpx_raw):
    try:
        gpx = gpxpy.parse(gpx_raw)
    except Exception as e:
        return f"Failed to parse GPX file: {str(e)}", 400

    return gpx


def http_post(api_url, headers, body):
    try:
        response = requests.post(api_url, headers=headers, json=body)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return f"API call failed: {str(e)}", 500

    return response


def get_route(long1, lat1, long2, lat2):
    api_url = 'https://api.openrouteservice.org/v2/directions/foot-hiking/gpx'
    headers = {
        'Authorization': '5b3ce3597851110001cf6248488e0d1ffe854d10ba214b419ba561d0',
        'Content-Type': 'application/json'
    }
    body = {
        'coordinates': [
            [long1, lat1],
            [long2, lat2]
        ]
    }
    response = http_post(api_url, headers, body)
    return parse_gpx(response.text)


def process_point_removal(gpx, longitude, latitude):
    route_start_idx, route_end_idx = find_routes_by_point(gpx, longitude, latitude)

    if route_start_idx == -1:
        # No start match, remove the ending route
        gpx.routes.pop(route_end_idx)
    else:
        # Merge routes and replace in list
        merge_routes(gpx, route_start_idx, route_end_idx)

    return gpx


def find_routes_by_point(gpx, longitude, latitude):
    route_start_with = -1
    route_end_with = -1
    for i, route in enumerate(gpx.routes):
        if points_match(route.points[0].longitude, longitude, route.points[0].latitude, latitude):
            route_start_with = i
        if points_match(route.points[-1].longitude, longitude, route.points[-1].latitude, latitude):
            route_end_with = i

    return route_start_with, route_end_with


def points_match(long1, long2, lat1, lat2):
    return (abs(long1 - long2) <= 0.00001 and
            abs(lat1 - lat2) <= 0.00001)


def merge_routes(gpx, start_idx, end_idx):
    start_point = gpx.routes[end_idx].points[0]
    end_point = gpx.routes[start_idx].points[-1]
    route_gpx = get_route(start_point.longitude, start_point.latitude, end_point.longitude, end_point.latitude)

    gpx.routes.pop(start_idx)
    gpx.routes.pop(end_idx)
    gpx.routes.insert(end_idx, route_gpx.routes[0])
