from services.ballistic_manager import BallisticManager
from services.projectile import DragModel

def verify():
    bm = BallisticManager()
    
    # 1. Fire North (Heading 0)
    print("Firing North...")
    res_n = bm.calculate_trajectory(
        lat=45.0, lon=0.0, altitude=0,
        velocity=1000, heading=0, climb_angle=45,
        projectile_params={"mass": 100, "caliber": 0.155, "bc": 2.0, "drag_model": DragModel.G1}
    )
    # Impact Latitude ~ 45 + change, Longitude should be > 0 (East Drift)
    impact_lon_n = res_n["telemetry"]["longitude"][-1]
    drift_n = impact_lon_n - 0.0
    print(f"North Fire Impact Lon change: {drift_n:.6f} deg")
    
    # 2. Fire South (Heading 180)
    print("Firing South...")
    res_s = bm.calculate_trajectory(
        lat=45.0, lon=0.0, altitude=0,
        velocity=1000, heading=180, climb_angle=45,
        projectile_params={"mass": 100, "caliber": 0.155, "bc": 2.0, "drag_model": DragModel.G1}
    )
    # Impact Latitude ~ 45 - change, Longitude should be > 0 (East Drift? Wait)
    # North Hemisphere firing South: Deflects Right (West).
    # Velocity is South (-y). Omega is (North, Up).
    # Omega x v = (Ny + Uz) x (-Sy) = N(-y x y) + U(z x -y) = 0 + U(x) = East.
    # Force = -2 m (East) = West.
    # So drift should be negative (West).
    impact_lon_s = res_s["telemetry"]["longitude"][-1]
    drift_s = impact_lon_s - 0.0
    print(f"South Fire Impact Lon change: {drift_s:.6f} deg")
    
    if drift_n > 0:
        print("PASS: North fire drifted East.")
    else:
        print("FAIL: North fire drift incorrect.")
        
    if drift_s < 0:
        print("PASS: South fire drifted West.")
    else:
        print("FAIL: South fire drift incorrect.")

if __name__ == "__main__":
    verify()
