import pytest
try:
    from ..services.weather_manager import WeatherManager
except ImportError:
    # allow running this test file directly (no package context)
    from weather_manager import WeatherManager

class TestWeatherManager:
    def test_convert_dms_to_dd_basic(self):
        wm = WeatherManager()
        assert wm._convert_DMS_to_DD("50-37N") == pytest.approx(50.6167, rel=1e-3)
    
    def test_convert_dms_to_dd_various_inputs(self):
        wm = WeatherManager()
        test_cases = [
            ("49-37N", 49.6167),
            ("06-13E", 6.2167),
            ("40-26N", 40.4333),
            ("74-00S", 74.0),
        ]
        for dms_input, expected_output in test_cases:
            assert wm._convert_DMS_to_DD(dms_input) == pytest.approx(expected_output, rel=1e-3)
    
    def test_convert_dms_to_dd_zero_minutes(self):
        wm = WeatherManager()
        assert wm._convert_DMS_to_DD("45-00N") == pytest.approx(45.0, rel=1e-3)
    
    def test_convert_dms_to_dd_high_precision(self):
        wm = WeatherManager()
        assert wm._convert_DMS_to_DD("51-30N") == pytest.approx(51.5, rel=1e-3)

if __name__ == "__main__":
    TestWeatherManager().test_convert_dms_to_dd_basic()
    TestWeatherManager().test_convert_dms_to_dd_various_inputs()
    TestWeatherManager().test_convert_dms_to_dd_zero_minutes()
    TestWeatherManager().test_convert_dms_to_dd_high_precision()
    print("All tests passed!")