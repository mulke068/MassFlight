import pytest
import math
from services.physics_engine import PhysicsEngine
from services.projectile import Projectile, DragModel

def test_wind_effects():
    pe = PhysicsEngine()
    proj = Projectile(mass_kg=50, caliber_m=0.155, ballistic_coefficient=2.0, drag_model=DragModel.G1)
    
    v_total = 800
    climb = 45
    heading = 0 # North
    
    vx = v_total * math.cos(math.radians(climb)) * math.sin(math.radians(heading)) # 0
    vy = v_total * math.cos(math.radians(climb)) * math.cos(math.radians(heading)) # 565.68
    vz = v_total * math.sin(math.radians(climb)) # 565.68
    
    velocity = (vx, vy, vz)
    start = (45.0, 0.0, 0.0)
    
    # Baseline
    res_base = pe.integrate_trajectory(*start, velocity, proj, weather_data=None)
    dist_base = res_base["summary"]["total_distance"]
    
    # Headwind
    w_head = {"wind": {"direction": "0", "speed": "50", "unit": "MPS"}}
    res_head = pe.integrate_trajectory(*start, velocity, proj, weather_data=w_head)
    dist_head = res_head["summary"]["total_distance"]
    
    assert dist_head < dist_base, "Headwind should reduce range"
    
    # Tailwind
    w_tail = {"wind": {"direction": "180", "speed": "50", "unit": "MPS"}}
    res_tail = pe.integrate_trajectory(*start, velocity, proj, weather_data=w_tail)
    dist_tail = res_tail["summary"]["total_distance"]
    
    assert dist_tail > dist_base, "Tailwind should increase range"
    
    # Crosswind
    w_cross = {"wind": {"direction": "270", "speed": "50", "unit": "MPS"}}
    res_cross = pe.integrate_trajectory(*start, velocity, proj, weather_data=w_cross)
    
    base_lon = res_base["telemetry"][-1]["longitude"]
    cross_lon = res_cross["telemetry"][-1]["longitude"]
    
    drift_deg = cross_lon - base_lon
    
    # Wind from West (270) -> Pushes East (+Lon)
    assert drift_deg > 0.01, f"Crosswind should cause East drift, got {drift_deg}"
