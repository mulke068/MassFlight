from services.physics_engine import PhysicsEngine
from services.projectile import Projectile, DragModel
import math

def verify():
    pe = PhysicsEngine()
    proj = Projectile(mass_kg=100, caliber_m=0.155, ballistic_coefficient=2.0, drag_model=DragModel.G7)
    
    v_total = 1000
    climb = 45
    heading = 90 # East
    
    # Vx, Vy, Vz for East shot
    # Vx = V * cos(climb) * sin(heading) = V * cos(45) * 1 = V * 0.707
    # Vy = V * cos(climb) * cos(heading) = V * cos(45) * 0 = 0
    # Vz = V * sin(climb)
    
    vx = v_total * math.cos(math.radians(climb)) * 1.0
    vy = 0.0
    vz = v_total * math.sin(math.radians(climb))
    velocity = (vx, vy, vz)
    
    print("--- Test 1: Equator Fire (0 deg Lat) ---")
    start_eq = (0.0, 0.0, 0.0)
    res_eq = pe.integrate_trajectory(*start_eq, velocity, proj)
    dist_eq = res_eq["summary"]["total_distance"]
    final_lon_eq = res_eq["telemetry"][-1]["longitude"]
    d_lon_eq = final_lon_eq - 0.0
    print(f"Distance: {dist_eq:.2f} m")
    print(f"Delta Lon: {d_lon_eq:.6f} deg")
    
    print("\n--- Test 2: High Lat Fire (60 deg Lat) ---")
    start_hi = (60.0, 0.0, 0.0)
    res_hi = pe.integrate_trajectory(*start_hi, velocity, proj)
    dist_hi = res_hi["summary"]["total_distance"]
    final_lon_hi = res_hi["telemetry"][-1]["longitude"]
    d_lon_hi = final_lon_hi - 0.0
    print(f"Distance: {dist_hi:.2f} m")
    print(f"Delta Lon: {d_lon_hi:.6f} deg")
    
    # Verification Logic
    # 1. Distances should be roughly similar (physics is local).
    # Note: Gravity might differ slightly due to latitude (WGS84).
    # Coriolis might differ.
    # But roughly similar.
    diff_dist = abs(dist_eq - dist_hi)
    print(f"\nDistance diff: {diff_dist:.2f} m")
    
    # 2. Longitude change should be different.
    # Cos(0) = 1. Cos(60) = 0.5.
    # dLon ~ Dist / (R * cos(lat))
    # dLon_hi should be approx 2 * dLon_eq
    ratio = d_lon_hi / d_lon_eq
    print(f"Ratio (Hi/Eq): {ratio:.2f} (Expected ~2.0)")
    
    if 1.9 < ratio < 2.1:
        print("PASS: Spherical metric confirmed (Ratio ~2.0).")
    else:
        print("FAIL: Ratio not close to 2.0.")

if __name__ == "__main__":
    verify()
