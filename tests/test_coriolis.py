import pytest
import math
from services.physics_engine import PhysicsEngine
from services.projectile import Projectile, DragModel
from config.core_config import EARTH_RADIUS_M

def test_coriolis_northern_hemisphere_north_shot():
    """Verify Eastward deflection for North shot in Northern Hemisphere."""
    pe = PhysicsEngine()
    
    # 45 deg North Latitude
    lat = 45.0
    # Firing North (vy > 0)
    vx, vy, vz = 0.0, 1000.0, 0.0 # Only horizontal North velocity
    
    ax, ay, az = pe._calculate_coriolis_acceleration(lat, vx, vy, vz)
    
    # Expected: Deflection to the Right (East). ax > 0.
    assert ax > 0, f"Expected Eastward drift (ax > 0), got {ax}"
    print(f"Northern/North Shot Accel: ({ax:.4f}, {ay:.4f}, {az:.4f})")

    # Separate check for Vertical shot
    vx, vy, vz = 0.0, 0.0, 1000.0
    ax, ay, az = pe._calculate_coriolis_acceleration(lat, vx, vy, vz)
    # Upward shot deflects West (ax < 0)
    assert ax < 0, f"Expected Westward drift for Up shot (ax < 0), got {ax}"

def test_coriolis_southern_hemisphere_north_shot():
    """Verify Westward deflection for North shot in Southern Hemisphere."""
    pe = PhysicsEngine()
    
    # 45 deg South Latitude
    lat = -45.0
    # Firing North (vy > 0)
    vx, vy, vz = 0.0, 1000.0, 1000.0
    
    ax, ay, az = pe._calculate_coriolis_acceleration(lat, vx, vy, vz)
    
    # Expected: Deflection to the Left (West). ax < 0.
    assert ax < 0, f"Expected Westward drift (ax < 0), got {ax}"
    print(f"Southern/North Shot Accel: ({ax:.4f}, {ay:.4f}, {az:.4f})")

def test_coriolis_equator_vertical_shot():
    """Verify Westward deflection for Vertical shot at Equator."""
    pe = PhysicsEngine()
    
    # Equator
    lat = 0.0
    # Firing Up (vz > 0)
    vx, vy, vz = 0.0, 0.0, 1000.0
    
    ax, ay, az = pe._calculate_coriolis_acceleration(lat, vx, vy, vz)
    
    # Expected: Deflection West (ax < 0) due to Earth rotating East under correct projectile?
    # Actually, Coriolis on upward moving body at equator: -2 * Omega x v
    # Omega = (0, Oy, 0) - wait, ENU at equator.
    # At equator (lat=0), Omega vector points North.
    # Omega = (0, Omega_earth, 0).
    # v = (0, 0, vz).
    # Cross product Omega x v = (Omega_y * vz, 0, 0)
    # a_cor = -2 * (Omega x v) = (-2 * Omega_y * vz, 0, 0)
    # So ax should be negative (West). Correct.
    
    assert ax < 0, f"Expected Westward drift (ax < 0) for vertical shot at equator, got {ax}"
