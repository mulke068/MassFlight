"""Unit tests for ballistic calculation module."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import math
from services.projectile import Projectile, DragModel
from services.physics_engine import PhysicsEngine
from services.ballistic_manager import BallisticManager

class TestBallistics(unittest.TestCase):

    def test_projectile_initialization(self):
        """Test projectile creation and derived properties."""
        p = Projectile(mass_kg=10.0, caliber_m=0.1, ballistic_coefficient=0.5)
        self.assertEqual(p.mass_kg, 10.0)
        self.assertAlmostEqual(p.area_m2, math.pi * 0.05**2)
        self.assertEqual(p.drag_model, DragModel.G1)

    def test_air_density(self):
        """Test air density calculation."""
        pe = PhysicsEngine()
        rho_sea = pe.calculate_air_density(0, 15, 1013.25)
        self.assertAlmostEqual(rho_sea, 1.225, places=2)
        
        rho_high = pe.calculate_air_density(10000, 15, 1013.25)
        self.assertLess(rho_high, rho_sea)

    def test_drag_force_direction(self):
        """Test that drag force opposes velocity."""
        pe = PhysicsEngine()
        p = Projectile(mass_kg=1.0, caliber_m=0.1, ballistic_coefficient=0.5)
        
        # Velocity moving East (x+)
        v = (100, 0, 0)
        rho = 1.225
        fx, fy, fz = pe.calculate_drag_force(v, rho, p)
        
        self.assertLess(fx, 0) # Drag should be negative x
        self.assertEqual(fy, 0)
        self.assertEqual(fz, 0)

    def test_trajectory_integration(self):
        """Test full trajectory integration."""
        bm = BallisticManager()
        
        # Fire straight up (90 deg climb)
        res = bm.calculate_trajectory(
            lat=0, lon=0, altitude=0,
            velocity=100,
            heading=0,
            climb_angle=90
        )
        
        summary = res["summary"]
        self.assertGreater(summary["max_altitude"], 0)
        self.assertAlmostEqual(summary["total_distance"], 0, delta=100) # Should land near start
        
        # Fire at 45 deg
        res_45 = bm.calculate_trajectory(
            lat=0, lon=0, altitude=0,
            velocity=100,
            heading=0,
            climb_angle=45
        )
        self.assertGreater(res_45["summary"]["total_distance"], 0)

if __name__ == '__main__':
    unittest.main()
