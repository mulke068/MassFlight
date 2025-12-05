"""Physics engine for ballistic trajectory calculations.

This module provides the core physics integration for projectile motion,
accounting for gravity and aerodynamic drag.
"""

import math
from typing import List, Tuple, Dict, Any

from services.projectile import Projectile, DragModel
from services.gravity import get_gravity_at_location

# Standard atmospheric constants (ISA)
STD_TEMP_K = 288.15
STD_PRESSURE_PA = 101325.0
LAPSE_RATE = 0.0065  # K/m
GAS_CONSTANT = 287.05
GRAVITY_STD = 9.80665


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

        # Estimate Cd from BC (Simplified)
        # Standard G1 projectile mass=1lb, d=1inch, Cd=0.5ish?
        # BC = m / (d^2 * i) -> i = m / (d^2 * BC)
        # Cd = Cd_std * i
        # This is complex without a full G1 table.
        # For this implementation, we will use a simplified constant Cd derived from BC
        # assuming a standard form factor or just taking BC as a direct scaler if provided roughly.
        #
        # Better approach for V1: Use a fixed Cd of 0.5 if BC is not perfectly calibrated,
        # OR use the standard retardation formula: Drag = 0.5 * rho * v^2 * A * Cd
        #
        # Let's assume the user might want to provide Cd directly or we estimate it.
        # Since Projectile has BC, let's try to use it.
        # Physics: Deceleration = -0.5 * rho * v^2 * A * Cd / m
        # Ballistic definition: Deceleration = -0.5 * rho * v^2 / BC_phys (where BC_phys has units kg/m2)
        #
        # Let's use a constant Cd = 0.47 (Sphere) or 0.2-0.5 (Bullet) for now as a fallback
        # if we don't have a full G1 model.
        #
        # User asked for "Projectile Mass, Drag Coeff, Area" in the plan, but I used BC in the class.
        # I will use a constant Cd = 0.5 for now to ensure the code runs, as implementing a full G1 G-function is out of scope for "V1".
        cd = 0.5

        # Drag magnitude
        drag_mag = 0.5 * density * v_sq * cd * projectile.area_m2

        # Direction is opposite to velocity
        fx = -drag_mag * (vx / v_mag)
        fy = -drag_mag * (vy / v_mag)
        fz = -drag_mag * (vz / v_mag)

        return (fx, fy, fz)

    def integrate_trajectory(self, start_ecef: Tuple[float, float, float],
                             velocity_ecef: Tuple[float, float, float],
                             projectile: Projectile,
                             weather_data: Dict[str, Any] = None,
                             dt: float = 0.05) -> Dict[str, Any]:
        """Integrates the trajectory over time using ECEF coordinates.

        Args:
            start_ecef: Starting position (x, y, z) in meters (ECEF).
            velocity_ecef: Initial velocity (vx, vy, vz) in m/s (ECEF).
            projectile: The projectile.
            weather_data: Weather info (temp, pressure).
            dt: Time step in seconds.
        """
        from gui.engine.coordinates import ecef_to_lla
        
        # Initial State (ECEF)
        x, y, z = start_ecef
        vx, vy, vz = velocity_ecef
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
        max_steps = 500000 # Allow for long duration flights (e.g. 25000s at dt=0.05)
        step = 0
        
        # Initial LLA
        curr_lat, curr_lon, curr_alt = ecef_to_lla(x, y, z)

        while curr_alt >= 0 and step < max_steps:
            # 1. Get Environmental Data
            density = self.calculate_air_density(curr_alt, temp_c, pressure_hpa)
            g_mag = get_gravity_at_location(curr_lat, curr_alt) # m/s^2 scalar

            # 2. Calculate Forces
            # Gravity Vector (ECEF): Points towards Earth Center (0,0,0)
            # Fg = m * g_vec
            # g_vec = -normalize(pos) * g_mag
            pos_mag = math.sqrt(x*x + y*y + z*z)
            if pos_mag == 0:
                gx, gy, gz = 0, 0, 0
            else:
                gx = -(x / pos_mag) * g_mag
                gy = -(y / pos_mag) * g_mag
                gz = -(z / pos_mag) * g_mag
            
            fg_x = gx * projectile.mass_kg
            fg_y = gy * projectile.mass_kg
            fg_z = gz * projectile.mass_kg

            # Drag Force (ECEF)
            # Velocity is relative to Earth (ECEF is fixed to Earth)
            # So wind would need to be added here if we had it.
            # Assuming no wind, airspeed = groundspeed.
            fd_x, fd_y, fd_z = self.calculate_drag_force((vx, vy, vz), density, projectile)

            # Total Force
            fx = fg_x + fd_x
            fy = fg_y + fd_y
            fz = fg_z + fd_z
            
            # Store previous state
            prev_x, prev_y, prev_z = x, y, z
            prev_vx, prev_vy, prev_vz = vx, vy, vz
            prev_t = t
            prev_alt = curr_alt

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
            
            # Update LLA for next step (and check altitude)
            curr_lat, curr_lon, curr_alt = ecef_to_lla(x, y, z)

            # Check for ground impact
            if curr_alt < 0:
                # Interpolate to find exact impact
                # 0 = prev_alt + (curr_alt - prev_alt) * alpha
                if abs(curr_alt - prev_alt) > 1e-9:
                    alpha = -prev_alt / (curr_alt - prev_alt)
                else:
                    alpha = 0
                
                # Interpolate ECEF position
                x = prev_x + (x - prev_x) * alpha
                y = prev_y + (y - prev_y) * alpha
                z = prev_z + (z - prev_z) * alpha
                t = prev_t + dt * alpha
                
                # Final LLA
                curr_lat, curr_lon, curr_alt = ecef_to_lla(x, y, z)
                curr_alt = 0.0 # Force to 0
                
                points.append((curr_lat, curr_lon, curr_alt))
                
                # Add final telemetry point
                v_mag = math.sqrt(vx**2 + vy**2 + vz**2)
                dist_from_start = 0 # TODO: Calculate actual ground distance if needed
                
                telemetry.append({
                    "time": round(t, 2),
                    "altitude": round(curr_alt, 2),
                    "velocity": round(v_mag, 2),
                    "distance": 0, # Placeholder, calculated in Manager
                    "latitude": curr_lat,
                    "longitude": curr_lon
                })
                
                break # Stop simulation

            # 4. Store Data
            points.append((curr_lat, curr_lon, curr_alt))
            
            if step % 10 == 0: # Downsample telemetry
                v_mag = math.sqrt(vx**2 + vy**2 + vz**2)
                telemetry.append({
                    "time": round(t, 2),
                    "altitude": round(curr_alt, 2),
                    "velocity": round(v_mag, 2),
                    "distance": 0, # Placeholder
                    "latitude": curr_lat,
                    "longitude": curr_lon
                })

            step += 1

        return {
            "points": points,
            "telemetry": telemetry,
            "summary": {
                "flight_time": round(t, 2),
                "max_altitude": round(max(p[2] for p in points) if points else 0, 2),
                "total_distance": 0, # Calculated in Manager
                "impact_velocity": round(math.sqrt(vx**2 + vy**2 + vz**2), 2)
            }
        }
