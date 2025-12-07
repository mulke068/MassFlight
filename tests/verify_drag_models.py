from services.physics_engine import PhysicsEngine
from services.projectile import Projectile, DragModel

def verify():
    pe = PhysicsEngine()
    
    # Check G1
    print("Checking G1...")
    cd_g1 = pe._get_drag_coefficient(1.0, DragModel.G1)
    print(f"G1 at Mach 1.0: {cd_g1}")
    
    # Check G7
    print("Checking G7...")
    try:
        cd_g7 = pe._get_drag_coefficient(1.0, DragModel.G7)
        print(f"G7 at Mach 1.0: {cd_g7}")
    except Exception as e:
        print(f"G7 Failed: {e}")

    # Check Unknown (Safety)
    print("Checking Unknown...")
    try:
        # Mock enum or force bad value if possible, strict typing makes it hard but runtime allows
        cd_bad = pe._get_drag_coefficient(1.0, "BAD_VALUE")
        print(f"Unknown at Mach 1.0: {cd_bad}")
    except Exception as e:
        print(f"Unknown Failed: {e}")

if __name__ == "__main__":
    verify()
