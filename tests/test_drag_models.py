import pytest
from services.physics_engine import PhysicsEngine
from services.projectile import DragModel

def test_g1_lookup():
    pe = PhysicsEngine()
    cd_g1 = pe._get_drag_coefficient(1.0, DragModel.G1)
    # G1 at Mach 1.0 is typically around 0.4-0.5 depending on table
    assert cd_g1 > 0.1
    assert cd_g1 < 1.0

def test_g7_lookup():
    pe = PhysicsEngine()
    cd_g7 = pe._get_drag_coefficient(1.0, DragModel.G7)
    # G7 at Mach 1.0
    assert cd_g7 > 0.1
    assert cd_g7 < 1.0

def test_unknown_drag_model_fallback():
    pe = PhysicsEngine()
    # Passing a string or invalid enum should fallback to G1 safely
    # Note: Type checker might complain but Python runtime allows it.
    cd_bad = pe._get_drag_coefficient(1.0, "BAD_VALUE")
    
    # Should equal G1 result
    cd_g1 = pe._get_drag_coefficient(1.0, DragModel.G1)
    assert cd_bad == cd_g1
