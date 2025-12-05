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
        LOG.debug(f"Calculating trajectory from {lat}, {lon} at {velocity} m/s")

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
        
        rad_heading = heading * (math.pi / 180)
        rad_climb = climb_angle * (math.pi / 180)
        
        vx = velocity * math.cos(rad_climb) * math.sin(rad_heading)
        vy = velocity * math.cos(rad_climb) * math.cos(rad_heading)
        vz = velocity * math.sin(rad_climb)

        # 3. Get Weather Data (Optional)
        # We try to get weather for the launch location
        weather_data = None
        try:
            # Note: WeatherManager.get returns (weather_dict, trys)
            if self.weather_manager.last_target_lat == lat and self.weather_manager.last_target_lon == lon:
                weather_data = self.weather_manager.weather
                LOG.debug("Weather data retrieved from cache.")
            else:
                weather_response, tries = self.weather_manager.get(lat, lon)
                if weather_response:
                    weather_data = weather_response
                    LOG.info(f"Weather data retrieved for simulation after {tries} tries.")
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
            scale_alt = (p_alt / EARTH_RADIUS_M) * SPHERE_RADIUS * 2 
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
            "latitude": [p[0] for p in simulation_result["points"][::10]],
            "longitude": [p[1] for p in simulation_result["points"][::10]]
        }
        # Note: Points are not downsampled in physics engine return, but telemetry is.
        # We need to be careful. Physics engine returns points for every step, telemetry every 10.
        # Let's just trust the telemetry dict keys.

        return {
            "visualization_points": viz_points,
            "telemetry": formatted_telemetry,
            "summary": simulation_result["summary"]
        }

    def solve_firing_solution(self,
                              lat: float,
                              lon: float,
                              alt: float,
                              target_lat: float,
                              target_lon: float,
                              climb_angle: float,
                              projectile_params: Dict[str, Any] = None,
                              progress_callback=None) -> Tuple[float, float]:
        """Solves for required Velocity and Heading to hit target (correcting for drift).

        Args:
            lat, lon, alt: Launch position.
            target_lat, target_lon: Target position.
            climb_angle: Fixed climb angle (deg).
            projectile_params: Projectile configuration.
            progress_callback: Optional function(int) to report progress %.

        Returns:
            Tuple (velocity, heading) or (None, None) if unreachable.
        """
        from gui.engine.coordinates import calculate_distance, calculate_bearing
        
        # Target Data
        target_dist_km = calculate_distance(lat, lon, target_lat, target_lon)
        target_dist_m = target_dist_km * 1000.0
        initial_heading = calculate_bearing(lat, lon, target_lat, target_lon)
        
        LOG.info(f"Solving 2D firing solution. Dist: {target_dist_m:.1f}m, Initial Heading: {initial_heading:.1f}")

        # Initial Guesses
        g = 9.81
        rad_angle = math.radians(climb_angle)
        sin_2theta = math.sin(2 * rad_angle)
        
        if abs(sin_2theta) < 1e-6:
             return 1000.0, initial_heading

        # Vacuum velocity guess
        v_guess = math.sqrt(target_dist_m * g / sin_2theta)
        heading_guess = initial_heading
        
        # Optimization Loop (Nested)
        # Outer Loop: Adjust Heading (to fix cross-track error/drift)
        # Inner Loop: Adjust Velocity (to fix range error)
        
        max_heading_iter = 50
        # heading_tolerance = 0.05 # degrees
        heading_tolerance = 0.001 # degrees (High Precision)
        
        for h_iter in range(max_heading_iter):
            
            # Report Progress
            if progress_callback: # TODO: Remove
                # Map iteration 0..max to 0..100%
                percent = int((h_iter / max_heading_iter) * 100)
                progress_callback(percent)

            # --- Inner Loop: Solve Velocity for current Heading ---
            v_solved = self._solve_velocity_for_heading(
                lat, lon, alt, heading_guess, climb_angle, projectile_params, target_dist_m, v_guess
            )
            
            if v_solved is None:
                LOG.warning("Velocity solver failed during heading optimization.")
                return None, None
            
            v_guess = v_solved # Update guess for next time
            
            # Check Lateral Error
            # We need the impact location.
            # Run one full simulation with best velocity and current heading
            res = self.calculate_trajectory(lat, lon, alt, v_solved, heading_guess, climb_angle, projectile_params)

            # We can get it from the last telemetry point (which we just added longitude to)
            impact_lat = res["telemetry"]["latitude"][-1]
            impact_lon = res["telemetry"]["longitude"][-1]
            
            # Calculate bearing from Launch to Impact
            impact_bearing = calculate_bearing(lat, lon, impact_lat, impact_lon)
            
            # Calculate Error: Target Bearing - Impact Bearing
            # Be careful with 360 wrap-around
            bearing_err = initial_heading - impact_bearing
            
            # Normalize error to -180 to 180
            while bearing_err > 180: bearing_err -= 360
            while bearing_err < -180: bearing_err += 360
            
            LOG.debug(f"Heading Iter {h_iter}: v={v_solved:.1f}, heading={heading_guess:.4f}, impact_bearing={impact_bearing:.4f}, err={bearing_err:.4f}")
            
            if abs(bearing_err) < heading_tolerance:
                LOG.info(f"2D Solution found: v={v_solved:.1f} m/s, heading={heading_guess:.4f}")
                if progress_callback: progress_callback(100) # TODO: Remove
                return v_solved, heading_guess
            
            # Apply Correction
            # If we hit to the RIGHT (impact > target), error is negative. We need to aim LEFT (decrease heading).
            # So adding error (negative) decreases heading. Correct.
            # Gain factor to prevent oscillation
            # gain = 1.0
            gain = 1.2 # TODO: Remove
            heading_guess += bearing_err * gain
            
        LOG.warning("Heading optimization did not fully converge.")
        if progress_callback: progress_callback(100) # TODO: Remove
        return v_solved, heading_guess

    def _solve_velocity_for_heading(self, lat, lon, alt, heading, climb, params, target_dist, v_guess):
        from gui.engine.coordinates import calculate_distance
        # Secant method for velocity
        v0 = v_guess
        v1 = v0 * 1.05
        
        MAX_VELOCITY = 50000.0 # Safety cap
        
        for i in range(15):
            # V0
            res0 = self.calculate_trajectory(lat, lon, alt, v0, heading, climb, params)
            # Use Great Circle Distance to match target_dist metric
            # dist0 = res0["summary"]["distance"]
            i_lat0 = res0["telemetry"]["latitude"][-1]
            i_lon0 = res0["telemetry"]["longitude"][-1]
            dist0 = calculate_distance(lat, lon, i_lat0, i_lon0) * 1000.0
            
            err0 = dist0 - target_dist
            
            if abs(err0) < 50.0: return v0
            
            # V1
            res1 = self.calculate_trajectory(lat, lon, alt, v1, heading, climb, params)
            # dist1 = res1["summary"]["distance"]
            i_lat1 = res1["telemetry"]["latitude"][-1]
            i_lon1 = res1["telemetry"]["longitude"][-1]
            dist1 = calculate_distance(lat, lon, i_lat1, i_lon1) * 1000.0
            
            err1 = dist1 - target_dist
            
            if abs(err1) < 50.0: return v1
            
            diff = err1 - err0
            # if abs(diff) < 1e-9
            if abs(diff) < 1e-6: # Prevent division by zero or huge jumps
                v_next = v1 * 1.05 + 10
            else:
                v_next = v1 - err1 * (v1 - v0) / diff
            
            # Safety Clamps
            if v_next < 10: v_next = 10
            if v_next > MAX_VELOCITY: v_next = MAX_VELOCITY
            
            # If we are stuck at max velocity, maybe we can't reach it?
            if v_next == MAX_VELOCITY and v1 == MAX_VELOCITY:
                 LOG.warning("Solver hit max velocity limit. Target might be out of range.")
                 return MAX_VELOCITY
            
            v0 = v1
            v1 = v_next
            
        return v1

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
