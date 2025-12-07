from services.ballistic_manager import BallisticManager
import time

def verify():
    bm = BallisticManager()
    
    print("--- Test: Status Callback in Solver ---")
    
    def my_progress(val):
        # Only print every 10% to reduce spam
        if val % 20 == 0:
            print(f"  [Progress Bar]: {val}%")
            
    def my_status(msg):
        print(f"[Status Update]: {msg}")
            
    # Solve for a target
    # We choose a target that requires some iteration
    # 20km away
    print("\nSolving for 20km target...")
    
    bm.solve_firing_solution(
        lat=0, lon=0, alt=0,
        target_lat=0, target_lon=0.2, # ~22km
        climb_angle=45,
        progress_callback=my_progress,
        status_callback=my_status
    )

if __name__ == "__main__":
    verify()
