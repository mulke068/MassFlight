import pytest
import math
from services.physics_engine import PhysicsEngine
from services.projectile import Projectile, DragModel
from config.core_config import EARTH_RADIUS_M

def test_spherical_longitude_scaling():
    """Verify that moving East at high latitude changes Longitude more than at Equator."""
    pe = PhysicsEngine()
    proj = Projectile(mass_kg=50, caliber_m=0.155, ballistic_coefficient=1.0, drag_model=DragModel.G1)
    
    # 1. Equator Shot (East)
    # Velocity 1000 m/s East
    # Expected dLon per second (radians) = V / R
    res_eq = pe.integrate_trajectory(start_lat=0, start_lon=0, start_alt=0, 
                                     velocity_vector=(1000, 0, 1000), 
                                     projectile=proj,
                                     dt=1.0)
    
    # Take first step
    p0 = res_eq["telemetry"][0]
    p1 = res_eq["telemetry"][1]
    d_lon_eq = p1["longitude"] - p0["longitude"]
    
    # 2. High Latitude Shot (East) at 60 deg
    # Expected dLon = V / (R * cos(60)) = V / (R * 0.5) = 2 * (V/R)
    res_hi = pe.integrate_trajectory(start_lat=60, start_lon=0, start_alt=0, 
                                     velocity_vector=(1000, 0, 1000), 
                                     projectile=proj,
                                     dt=1.0) # Larger dt to capture difference in one step if possible, or check telemetry
    
    p0_hi = res_hi["telemetry"][0]
    p1_hi = res_hi["telemetry"][1]
    d_lon_hi = p1_hi["longitude"] - p0_hi["longitude"]
    
    ratio = d_lon_hi / d_lon_eq
    print(f"Ratio of dLon (60deg / 0deg): {ratio}")
    
    # Should be roughly 2.0 (1/cos(60))
    # Allow some margin for integration method (Euler)
    assert 1.9 < ratio < 2.1
