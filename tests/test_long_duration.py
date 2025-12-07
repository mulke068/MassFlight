import pytest
from services.physics_engine import PhysicsEngine
from services.projectile import Projectile, DragModel
from config.core_config import MAX_STEPS

def test_long_duration_flight():
    """Verify that flight duration extends beyond old 100k step limit."""
    pe = PhysicsEngine()
    
    # 1. High Velocity -> Long Duration
    # Velocity 7500 m/s (Orbital/ICBM range) at 45 deg
    # Should stay aloft for > 3000 seconds -> 300,000 steps at dt=0.01
    
    proj = Projectile(mass_kg=1000, caliber_m=0.5, ballistic_coefficient=5.0, drag_model=DragModel.G1)
    
    # 7000 m/s Up/East
    vx = 5000
    vz = 5500 # Tuned to ensure > 100,000 steps but < 5,000,000 (avoid orbit)
    vy = 0
    
    res = pe.integrate_trajectory(start_lat=0, start_lon=0, start_alt=0, 
                                     velocity_vector=(vx, vy, vz), 
                                     projectile=proj,
                                     dt=0.01) # 100 Hz
    
    steps_taken = len(res["points"])
    flight_time = res["summary"]["flight_time"]
    
    print(f"Steps: {steps_taken}, Time: {flight_time}s")
    
    # Check if we exceeded the old limit of 100,000
    assert steps_taken > 100000, f"Flight terminated too early: {steps_taken} steps"
    
    # Ensure we didn't hit MAX_STEPS hard limit (unless physics dictates it)
    # 5M limit is very high.
    assert steps_taken < MAX_STEPS, "Flight hit MAX_STEPS limit (stuck loop?)"
