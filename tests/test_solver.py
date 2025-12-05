import sys
import os
import logging

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from services.ballistic_manager import BallisticManager

logging.basicConfig(level=logging.INFO)

def test_solver():
    bm = BallisticManager()
    
    # Test Case: 10km shot
    # Start: 0,0
    # Target: 0, 0.1 (approx 11km East)
    
    start_lat = 0
    start_lon = 0
    target_lat = 0
    target_lon = 0.1 # ~11.1km
    
    print(f"Testing Solver: Start({start_lat},{start_lon}) -> Target({target_lat},{target_lon})")
    
    # Solve for 45 degrees
    velocity = bm.solve_firing_solution(
        lat=start_lat,
        lon=start_lon,
        alt=0,
        target_lat=target_lat,
        target_lon=target_lon,
        climb_angle=45
    )
    
    if velocity:
        print(f"Solver returned Velocity: {velocity:.2f} m/s")
        
        # Verify
        res = bm.calculate_trajectory(
            lat=start_lat,
            lon=start_lon,
            altitude=0,
            velocity=velocity,
            heading=90, # East
            climb_angle=45
        )
        
        dist = res["summary"]["total_distance"]
        print(f"Simulated Distance: {dist:.2f} m")
        
        # Calculate expected distance
        from gui.engine.coordinates import calculate_distance
        expected_km = calculate_distance(start_lat, start_lon, target_lat, target_lon)
        expected_m = expected_km * 1000.0
        print(f"Target Distance: {expected_m:.2f} m")
        
        error = abs(dist - expected_m)
        print(f"Error: {error:.2f} m")
        
        if error < 50:
            print("SUCCESS: Target hit within tolerance.")
        else:
            print("FAILURE: Target missed.")
    else:
        print("FAILURE: Solver could not find a solution.")

if __name__ == "__main__":
    test_solver()
