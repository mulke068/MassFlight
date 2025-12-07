"""Physics engine for ballistic trajectory calculations.

This module provides the core physics integration for projectile motion,
accounting for gravity and aerodynamic drag.
"""

import math
from typing import List, Tuple, Dict, Any

from config.core_config import (
    STD_TEMP_K,
    STD_PRESSURE_PA,
    LAPSE_RATE,
    GAS_CONSTANT,
    GRAVITY_STD
)
from services.projectile import Projectile, DragModel
from services.gravity import get_gravity_at_location


class PhysicsEngine:
    """Core physics engine for calculating projectile trajectories."""

    def __init__(self):
        """Initializes the physics engine."""
        pass

    def calculate_air_density(self, altitude_m: float, temperature_c: float = 15.0,
                              pressure_hpa: float = 1013.25) -> float:
        """Calculates air density based on altitude and local weather.

        Uses a simplified ISA model adjusted for local temperature and pressure.

        Args:
            altitude_m: Altitude in meters.
            temperature_c: Local temperature in Celsius (at sea level equivalent).
            pressure_hpa: Local pressure in hPa (at sea level equivalent).

        Returns:
            Air density in kg/m^3.
        """
        # Convert inputs to SI
        temp_k = temperature_c + 273.15
        pressure_pa = pressure_hpa * 100.0

        # Adjust for altitude (Troposphere model)
        if altitude_m < 11000:
            temperature_at_alt = temp_k - (LAPSE_RATE * altitude_m)
            pressure_at_alt = pressure_pa * (
                (1 - (LAPSE_RATE * altitude_m) / temp_k) ** (GRAVITY_STD / (LAPSE_RATE * GAS_CONSTANT))
            )
        else:
            # Simplified Stratosphere (constant temp)
            temperature_at_alt = temp_k - (LAPSE_RATE * 11000)
            pressure_11k = pressure_pa * (
                (1 - (LAPSE_RATE * 11000) / temp_k) ** (GRAVITY_STD / (LAPSE_RATE * GAS_CONSTANT))
            )
            pressure_at_alt = pressure_11k * math.exp(
                -GRAVITY_STD * (altitude_m - 11000) / (GAS_CONSTANT * temperature_at_alt)
            )

        density = pressure_at_alt / (GAS_CONSTANT * temperature_at_alt)
        return max(0.0, density)

    def calculate_drag_force(self, velocity_vector: Tuple[float, float, float],
                             density: float, projectile: Projectile) -> Tuple[float, float, float]:
        """Calculates the drag force vector.

        F_drag = 0.5 * rho * v^2 * Cd * A * -unit_velocity

        Args:
            velocity_vector: (vx, vy, vz) in m/s.
            density: Air density in kg/m^3.
            projectile: The projectile object.

        Returns:
            (fx, fy, fz) drag force vector in Newtons.
        """
        vx, vy, vz = velocity_vector
        v_sq = vx**2 + vy**2 + vz**2
        v_mag = math.sqrt(v_sq)

        if v_mag == 0:
            return (0.0, 0.0, 0.0)

        cd = 0.5

        # Drag magnitude
        drag_mag = 0.5 * density * v_sq * cd * projectile.area_m2

        # Direction is opposite to velocity
        fx = -drag_mag * (vx / v_mag)
        fy = -drag_mag * (vy / v_mag)
        fz = -drag_mag * (vz / v_mag)

        return (fx, fy, fz)

    def integrate_trajectory(self, start_lat: float, start_lon: float, start_alt: float,
                             velocity_vector: Tuple[float, float, float],
                             projectile: Projectile,
                             weather_data: Dict[str, Any] = None,
                             dt: float = 0.01) -> Dict[str, Any]:
        """Integrates the trajectory over time.

        Args:
            start_lat: Starting latitude (deg).
            start_lon: Starting longitude (deg).
            start_alt: Starting altitude (m).
            velocity_vector: Initial velocity (vx, vy, vz) in m/s (ECEF or local tangent?
                             For simplicity, let's assume local tangent: x=East, y=North, z=Up).
            projectile: The projectile.
            weather_data: Weather info (temp, pressure).
            dt: Time step in seconds.
        """
        # Initial State
        x, y, z = 0.0, 0.0, start_alt  # Local coordinates relative to launch (flat earth approx for physics step, mapped later)
        vx, vy, vz = velocity_vector
        t = 0.0

        points = []
        telemetry = []

        # Weather defaults
        temp_c = 15.0
        pressure_hpa = 1013.25
        if weather_data:
            if weather_data.get("temperature"):
                 temp_c = float(weather_data["temperature"]["value"])
            if weather_data.get("pressure"):
                 pressure_hpa = float(weather_data["pressure"]["value"])

        # Loop
        max_steps = 100000
        step = 0

        while z >= 0 and step < max_steps:
            # 1. Get Environmental Data
            density = self.calculate_air_density(z, temp_c, pressure_hpa)
            gravity = get_gravity_at_location(start_lat, z) # m/s^2 down

            # 2. Calculate Forces
            # Gravity acts down (-z)
            fg_z = -gravity * projectile.mass_kg

            # Drag
            fd_x, fd_y, fd_z = self.calculate_drag_force((vx, vy, vz), density, projectile)

            # Total Force
            fx = fd_x
            fy = fd_y
            fz = fg_z + fd_z

            # Check for ground impact
            if z < 0:
                # Linear Interpolation to find exact impact time
                # z_prev was >= 0, z is < 0
                # fraction of time step: alpha = (0 - z_prev) / (z - z_prev)
                # But we updated variables in place. We need previous values.
                # Let's store prev values before update?
                # Or just reverse interpolate:
                # z_current is z, z_prev is z - vz * dt (approx)
                
                # Better: Store previous state at start of loop
                pass 
            
            # ... actually, let's restructure the loop slightly to be cleaner
            
            # Store previous state
            prev_x, prev_y, prev_z = x, y, z
            prev_vx, prev_vy, prev_vz = vx, vy, vz
            prev_t = t

            # 3. Integrate (Euler)
            ax = fx / projectile.mass_kg
            ay = fy / projectile.mass_kg
            az = fz / projectile.mass_kg

            vx += ax * dt
            vy += ay * dt
            vz += az * dt

            x += vx * dt
            y += vy * dt
            z += vz * dt
            t += dt

            # Check for ground impact
            if z < 0:
                # Interpolate
                # 0 = prev_z + (z - prev_z) * alpha
                # alpha = -prev_z / (z - prev_z)
                if abs(z - prev_z) > 1e-9:
                    alpha = -prev_z / (z - prev_z)
                else:
                    alpha = 0
                
                # Interpolate position
                x = prev_x + (x - prev_x) * alpha
                y = prev_y + (y - prev_y) * alpha
                z = 0.0 # Force to 0
                t = prev_t + dt * alpha
                
                # Interpolate velocity (optional, but good for stats)
                vx = prev_vx + (vx - prev_vx) * alpha
                vy = prev_vy + (vy - prev_vy) * alpha
                vz = prev_vz + (vz - prev_vz) * alpha
                
                # Final Point
                d_lat = (y / 111111.0)
                d_lon = (x / (111111.0 * math.cos(math.radians(start_lat))))
                curr_lat = start_lat + d_lat
                curr_lon = start_lon + d_lon
                
                points.append((curr_lat, curr_lon, z))
                
                # Add final telemetry point
                telemetry.append({
                    "time": round(t, 2),
                    "altitude": round(z, 2),
                    "velocity": round(math.sqrt(vx**2 + vy**2 + vz**2), 2),
                    "distance": round(math.sqrt(x**2 + y**2), 2),
                    "latitude": curr_lat,
                    "longitude": curr_lon,
                    "gravity": round(gravity, 6)
                })
                
                break # Stop simulation

            # 4. Store Data
            # Convert local (x=East, y=North) to Lat/Lon updates
            # 1 deg lat ~ 111km, 1 deg lon ~ 111km * cos(lat)
            # This is a small angle approximation valid for short flights.
            # For ICBMs, we'd need full ECEF.
            d_lat = (y / 111111.0)
            d_lon = (x / (111111.0 * math.cos(math.radians(start_lat))))

            curr_lat = start_lat + d_lat
            curr_lon = start_lon + d_lon

            points.append((curr_lat, curr_lon, z))
            
            if step % 10 == 0: # Downsample telemetry
                telemetry.append({
                    "time": round(t, 2),
                    "altitude": round(z, 2),
                    "velocity": round(math.sqrt(vx**2 + vy**2 + vz**2), 2),
                    "distance": round(math.sqrt(x**2 + y**2), 2),
                    "latitude": curr_lat,
                    "longitude": curr_lon,
                    "gravity": round(gravity, 6)
                })

            step += 1

        return {
            "points": points,
            "telemetry": telemetry,
            "summary": {
                "flight_time": round(t, 2),
                "max_altitude": round(max(p[2] for p in points) if points else 0, 2),
                "total_distance": round(math.sqrt(x**2 + y**2), 2),
                "impact_velocity": round(math.sqrt(vx**2 + vy**2 + vz**2), 2)
            }
        }
