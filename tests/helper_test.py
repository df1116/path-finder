from unittest.mock import patch, MagicMock
from helper import parse_gpx, http_post, get_route, process_point_removal
import requests


def test_parse_gpx_success():
    # Assume gpx_raw is a well-formed GPX data string
    gpx_raw = "<gpx></gpx>"
    result = parse_gpx(gpx_raw)
    assert result  # check if parsing returned an object (non-empty)


def test_parse_gpx_failure():
    # Assume gpx_raw is a malformed GPX data string
    gpx_raw = "<gpx><error></gpx>"
    result, status_code = parse_gpx(gpx_raw)
    assert "Failed to parse GPX file:" in result
    assert status_code == 400


@patch('requests.post')
def test_http_post_success(mock_post):
    mock_post.return_value = MagicMock(status_code=200, text="success")
    mock_post.return_value.raise_for_status = MagicMock()
    api_url = "http://example.com/api"
    headers = {'Content-Type': 'application/json'}
    body = {'key': 'value'}
    response = http_post(api_url, headers, body)
    assert response.text == "success"


@patch('requests.post')
def test_http_post_failure(mock_post):
    mock_post.return_value = MagicMock(status_code=400)
    mock_post.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError("error")
    api_url = "http://example.com/api"
    headers = {'Content-Type': 'application/json'}
    body = {'key': 'value'}
    response, status_code = http_post(api_url, headers, body)
    assert "API call failed:" in response
    assert status_code == 500


def test_get_route():
    with patch('helper.http_post') as mock_post, patch('helper.parse_gpx') as mock_parse:
        mock_post.return_value.text = "<gpx></gpx>"
        mock_parse.return_value = "Parsed GPX Object"
        long1, lat1, long2, lat2 = 10.0, 20.0, 10.1, 20.1
        result = get_route(long1, lat1, long2, lat2)
        assert result == "Parsed GPX Object"


def test_process_point_removal():
    # Here you would need a mock or a fixture of a gpx object
    # Assuming the mock_gpx object has methods and attributes to interact with
    mock_gpx = MagicMock()
    mock_gpx.routes = [MagicMock(), MagicMock()]
    route_start_idx = 0
    route_end_idx = 1
    with patch('helper.find_routes_by_point', return_value=(route_start_idx, route_end_idx)), \
            patch('helper.merge_routes'):
        result = process_point_removal(mock_gpx, 10.0, 20.0)
        assert result  # Assuming processing changes the gpx object in some way
