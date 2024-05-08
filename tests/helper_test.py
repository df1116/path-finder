from flaskr.helper import parse_gpx


def test_parse_gpx_success():
    gpx_raw = "<gpx></gpx>"
    result = parse_gpx(gpx_raw)
    assert result
