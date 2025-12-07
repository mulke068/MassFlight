import pytest
from services.ballistic_manager import BallisticManager

def test_progress_callback():
    bm = BallisticManager()
    
    progress_values = []
    
    def my_callback(val):
        progress_values.append(val)
            
    # Fire a shot that should take some steps
    # High speed to ensure enough steps
    bm.calculate_trajectory(
        lat=0, lon=0, altitude=0,
        velocity=7500, heading=90, climb_angle=45,
        progress_callback=my_callback
    )
    
    assert len(progress_values) > 0, "Progress callback was never called"
    assert progress_values[-1] > 0, "Final progress value should be > 0"
    # Check that it increments (not strictly monotonic if reset, but generally)
    # But since this is a single trajectory, it should be Monotonic? 
    # Yes, for calculate_trajectory it scales 0-100 based on steps.
    assert sorted(progress_values) == progress_values, "Progress should be monotonic"
