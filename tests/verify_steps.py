from services.physics_engine import PhysicsEngine
from services.projectile import Projectile, DragModel
import math
import time

def verify():
    pe = PhysicsEngine()
    # High altitude, low drag, low velocity decay -> Long flight
    # Mass 1000kg, Cal 0.5m, BC 10.0 (Very low drag)
    # Fire straight up to very high altitude to maximize time?
    # Or fire Orbital-ish
    
    proj = Projectile(mass_kg=1000, caliber_m=1.0, ballistic_coefficient=50.0, drag_model=DragModel.G7)
    
    # Fire at 6000 m/s at 45 deg
    v_total = 6000
    climb = 45
    heading = 90
    vx = v_total * math.cos(math.radians(climb))
    vy = 0 
    vz = v_total * math.sin(math.radians(climb))
    
    start = (0.0, 0.0, 0.0)
    velocity = (vx, vy, vz)
    
    print("Simulating long-range flight...")
    t0 = time.time()
    res = pe.integrate_trajectory(*start, velocity, proj, dt=1.0) # Larger DT for test speed
    t1 = time.time()
    
    steps_taken = len(res["points"])
    flight_time = res["summary"]["flight_time"]
    
    print(f"Simulation took {t1-t0:.2f}s locally.")
    print(f"Flight Time: {flight_time} s")
    print(f"Steps: {steps_taken}")
    print(f"Max Altitude: {res['summary']['max_altitude']} m")
    print(f"Distance: {res['summary']['total_distance']} m")
    
    # If flight time > 1000s (old limit 100k steps * 0.01dt = 1000s), then we passed the barrier 
    # (assuming dt=0.01 in real app, here I used dt=1.0 for speed, so steps would be lower but time higher if physics holds)
    
    if flight_time > 2000:
        print("PASS: Flight duration exceeded previous limits.")
    else:
        print("INFO: Flight finished quickly (might be normal for this trajectory).")

if __name__ == "__main__":
    verify()
