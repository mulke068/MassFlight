from services.physics_engine import PhysicsEngine
from services.projectile import Projectile, DragModel
import math

def verify():
    pe = PhysicsEngine()
    
    # Setup standard projectile
    proj = Projectile(mass_kg=50, caliber_m=0.155, ballistic_coefficient=2.0, drag_model=DragModel.G1)
    
    # Launch Parameters: Firing North (vy=800, vx=0, vz=800)
    # 45 deg climb, 800 m/s total? roughly v_total ~ 1131. Let's precise.
    # vel = 800. climb=45. v_z = 800*sin(45)=565. v_ground=565. Heading=0 (North) -> v_y=565, v_x=0.
    v_total = 800
    climb = 45
    heading = 0 # North
    
    vx = v_total * math.cos(math.radians(climb)) * math.sin(math.radians(heading)) # 0
    vy = v_total * math.cos(math.radians(climb)) * math.cos(math.radians(heading)) # 565.68
    vz = v_total * math.sin(math.radians(climb)) # 565.68
    
    velocity = (vx, vy, vz)
    start = (45.0, 0.0, 0.0)
    
    print("--- Baseline (No Wind) ---")
    res_base = pe.integrate_trajectory(*start, velocity, proj, weather_data=None)
    dist_base = res_base["summary"]["total_distance"]
    print(f"Distance: {dist_base} m")
    
    print("\n--- Headwind (Wind From North, 50 m/s) ---")
    # Wind From North = 0 deg. Speed 50 m/s (approx 100 kts).
    # Expected: Shorter distance.
    w_head = {"wind": {"direction": "0", "speed": "50", "unit": "MPS"}}
    res_head = pe.integrate_trajectory(*start, velocity, proj, weather_data=w_head)
    dist_head = res_head["summary"]["total_distance"]
    print(f"Distance: {dist_head} m")
    
    print("\n--- Tailwind (Wind From South, 50 m/s) ---")
    # Wind From South = 180 deg.
    # Expected: Longer distance.
    w_tail = {"wind": {"direction": "180", "speed": "50", "unit": "MPS"}}
    res_tail = pe.integrate_trajectory(*start, velocity, proj, weather_data=w_tail)
    dist_tail = res_tail["summary"]["total_distance"]
    print(f"Distance: {dist_tail} m")
    
    print("\n--- Crosswind (Wind From West, 50 m/s) ---")
    # Wind From West = 270 deg.
    # Expected: Drift East (positive Longitude/X).
    w_cross = {"wind": {"direction": "270", "speed": "50", "unit": "MPS"}}
    res_cross = pe.integrate_trajectory(*start, velocity, proj, weather_data=w_cross)
    
    # PhysicsEngine returns telemetry as a LIST of dicts
    final_point_base = res_base["telemetry"][-1]
    final_point_cross = res_cross["telemetry"][-1]
    
    base_lon = final_point_base["longitude"]
    cross_lon = final_point_cross["longitude"]
    
    drift_deg = cross_lon - base_lon
    print(f"Baseline Lon: {base_lon:.6f}")
    print(f"Crosswind Lon: {cross_lon:.6f}")
    print(f"Net Drift: {drift_deg:.6f} deg")
    
    # Assertions
    if dist_head < dist_base:
        print("PASS: Headwind reduced range.")
    else:
        print("FAIL: Headwind did not reduce range.")
        
    if dist_tail > dist_base:
        print("PASS: Tailwind increased range.")
    else:
        print("FAIL: Tailwind did not increase range.")
        
    if drift_deg > 0.01: # Significant East drift
        print("PASS: Crosswind caused East drift.")
    else:
        print(f"FAIL: Crosswind drift too small ({drift_deg}).")

if __name__ == "__main__":
    verify()
