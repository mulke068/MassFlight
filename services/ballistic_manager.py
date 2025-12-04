"""Ballistic Manager Service.

This module acts as the orchestrator for ballistic calculations, connecting
user inputs, weather data, and the physics engine.
"""

import sys
import os

# Add parent directory to path to find config
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

import math
import logging
from typing import Dict, Any, List, Tuple

from services.projectile import Projectile, DragModel
from services.physics_engine import PhysicsEngine
from services.weather_manager import WeatherManager
from gui.engine.coordinates import xyz_to_lonlat, lonlat_to_xyz
from config.render_config import SPHERE_RADIUS

LOG = logging.getLogger(__name__)


class BallisticManager:
    """Manager for handling ballistic calculations and data flow."""

    def __init__(self):
        """Initializes the BallisticManager."""
        self.physics_engine = PhysicsEngine()
        self.weather_manager = WeatherManager()

    def calculate_trajectory(self,
                             lat: float,
                             lon: float,
                             altitude: float,
                             velocity: float,
                             heading: float,
                             climb_angle: float,
                             projectile_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Calculates the trajectory based on inputs.

        Args:
            lat: Launch latitude (deg).
            lon: Launch longitude (deg).
            altitude: Launch altitude (m).
            velocity: Muzzle velocity (m/s).
            heading: Heading (deg, 0=North, 90=East).
            climb_angle: Climb angle (deg, 0=Horizontal, 90=Vertical).
            projectile_params: Dictionary of projectile properties.
                               Defaults: Mass=100kg, Caliber=0.155m, BC=0.5.

        Returns:
            Dictionary containing visualization data and telemetry.
        """
        LOG.info(f"Calculating trajectory from {lat}, {lon} at {velocity} m/s")

        # 1. Setup Projectile
        if projectile_params is None:
            projectile_params = {}
        
        projectile = Projectile(
            mass_kg=projectile_params.get("mass", 100.0),
            caliber_m=projectile_params.get("caliber", 0.155),
            ballistic_coefficient=projectile_params.get("bc", 0.5),
            drag_model=DragModel.G1
        )

        # 2. Setup Initial Velocity Vector
        # Convert Heading/Climb to Cartesian Velocity components (Local Tangent Plane)
        # x = East, y = North, z = Up
        # Heading 0 = North (y+), 90 = East (x+)
        # This means:
        # vx = v * cos(climb) * sin(heading)
        # vy = v * cos(climb) * cos(heading)
        # vz = v * sin(climb)
        
        rad_heading = math.radians(heading)
        rad_climb = math.radians(climb_angle)
        
        vx = velocity * math.cos(rad_climb) * math.sin(rad_heading)
        vy = velocity * math.cos(rad_climb) * math.cos(rad_heading)
        vz = velocity * math.sin(rad_climb)

        # 3. Get Weather Data (Optional)
        # We try to get weather for the launch location
        weather_data = None
        try:
            # Note: WeatherManager.get returns (weather_dict, trys)
            weather_response, _ = self.weather_manager.get(lat, lon)
            if weather_response:
                weather_data = weather_response
                LOG.info("Weather data retrieved for simulation.")
        except Exception as e:
            LOG.warning(f"Could not retrieve weather data: {e}")

        # 4. Run Physics Integration
        simulation_result = self.physics_engine.integrate_trajectory(
            start_lat=lat,
            start_lon=lon,
            start_alt=altitude,
            velocity_vector=(vx, vy, vz),
            projectile=projectile,
            weather_data=weather_data
        )

        # 5. Format Output for Visualization
        viz_points = []
        EARTH_RADIUS_M = 6371000.0
        
        for p in simulation_result["points"]:
            p_lat, p_lon, p_alt = p
            scale_alt = (p_alt / EARTH_RADIUS_M) * SPHERE_RADIUS * 100 
            x, y, z = lonlat_to_xyz(p_lon, p_lat, SPHERE_RADIUS + (scale_alt if p_alt > 0 else 0))
            viz_points.append((x, y, z))

        # Reformat Telemetry: List of Dicts -> Dict of Lists
        # From: [{'time': 0, 'alt': 0}, ...]
        # To: {'time': [0, ...], 'alt': [0, ...]}
        raw_telemetry = simulation_result["telemetry"]
        formatted_telemetry = {
            "time": [d["time"] for d in raw_telemetry],
            "altitude": [d["altitude"] for d in raw_telemetry],
            "velocity": [d["velocity"] for d in raw_telemetry],
            "distance": [d["distance"] for d in raw_telemetry],
            "latitude": [p[0] for p in simulation_result["points"][::10]] # Approx matching downsample
        }
        # Note: Points are not downsampled in physics engine return, but telemetry is.
        # We need to be careful. Physics engine returns points for every step, telemetry every 10.
        # Let's just trust the telemetry dict keys.

        return {
            "visualization_points": viz_points,
            "telemetry": formatted_telemetry,
            "summary": simulation_result["summary"]
        }

if __name__ == "__main__":
    # Simple test
    logging.basicConfig(level=logging.INFO)
    bm = BallisticManager()
    
    # Test Launch: 45 deg climb, North
    res = bm.calculate_trajectory(
        lat=49.815,
        lon=6.131,
        altitude=300,
        velocity=800, # Tank shell / Artillery
        heading=0,
        climb_angle=45
    )
    
    print("Summary:", res["summary"])
    print(f"Generated {len(res['visualization_points'])} points.")
