from services.ballistic_manager import BallisticManager
from services.projectile import DragModel

def verify():
    bm = BallisticManager()
    
    # Test G1
    print("Testing G1...")
    res_g1 = bm.calculate_trajectory(
        lat=49.815, lon=6.131, altitude=300,
        velocity=800, heading=0, climb_angle=45,
        projectile_params={"mass": 100, "caliber": 0.155, "bc": 0.5, "drag_model": DragModel.G1}
    )
    print(f"Summary G1: {res_g1['summary']}")
    assert res_g1["summary"].get("drag_model") == "G1" or res_g1["summary"].get("drag_model") == "DragModel.G1"

    # Test G7
    print("Testing G7...")
    res_g7 = bm.calculate_trajectory(
        lat=49.815, lon=6.131, altitude=300,
        velocity=800, heading=0, climb_angle=45,
        projectile_params={"mass": 100, "caliber": 0.155, "bc": 0.5, "drag_model": DragModel.G7}
    )
    print(f"Summary G7: {res_g7['summary']}")
    assert res_g7["summary"].get("drag_model") == "G7" or res_g7["summary"].get("drag_model") == "DragModel.G7"
    
    print("Verification Passed.")

if __name__ == "__main__":
    verify()
