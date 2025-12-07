import pytest
from services.ballistic_manager import BallisticManager

def test_status_callback():
    bm = BallisticManager()
    
    status_messages = []
    
    def my_status(msg):
        status_messages.append(msg)
            
    # Solve for a target
    # 20km away
    bm.solve_firing_solution(
        lat=0, lon=0, alt=0,
        target_lat=0, target_lon=0.2, # ~22km
        climb_angle=45,
        status_callback=my_status
    )
    
    assert len(status_messages) > 0, "Status callback was never called"
    # Check format
    assert any("Iter" in msg for msg in status_messages), "Status message should contain iteration info"
    assert any("Verifying" in msg for msg in status_messages), "Status message should contain verification phase"
