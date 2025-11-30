import pytest
from services.weather_manager import WeatherManager

@pytest.fixture(scope="module")
def wm():
    return WeatherManager()
    
# @pytest
def test_luxembourg_station(wm):
    station_code, distance = wm._find_station(49.8157635,6.1315139999999815)
    assert station_code == "ELLX"
    assert distance < 23 # 22.969454057426283
    # data = wm.get(49.8157635, 6.1315139999999815)
    # assert data["station"]["code"] == "ELLX"  # Luxembourg
    # assert isinstance(data, dict)

def test_paris_station(wm):
    station_code, distance = wm._find_station(48.846659, 2.349194)
    assert station_code == "LFPW"  # Paris
    assert distance < 2
#     data = wm.get(48.846659, 2.349194)
#     assert data["station"]["code"] == "LFPW"  # Paris
#     assert isinstance(data, dict)

def test_tokyo_station(wm):
    station_code, distance = wm._find_station(35.675978, 139.721296)
    assert station_code == "RJTD"  # Tokyo
    assert distance < 5
#     data = wm.get(35.675978, 139.721296)
#     assert data["station"]["code"] == "RJTD"  # Tokyo
#     assert isinstance(data, dict)

def test_buenos_aires_station(wm):
    station_code , distance = wm._find_station(-34.776794, -58.385598)
    assert station_code == "SAEZ"  # Buenos Aires
    assert distance < 15
#     data = wm.get(-34.776794, -58.385598)
#     assert data["station"]["code"] == "SAEZ"  # Buenos Aires
#     assert isinstance(data, dict)