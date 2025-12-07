from assets.ballistics_tables import G7_DRAG_TABLE
from assets.ballistics_tables import G1_DRAG_TABLE
import math
from typing import List, Tuple, Dict, Any

from config.core_config import (
    STD_PRESSURE_HPA,
    STD_TEMP_C,
    LAPSE_RATE,
    GAS_CONSTANT,
    GRAVITY_STD,
    EARTH_OMEGA,
    MAX_STEPS,
    EARTH_RADIUS_M
)
from services.projectile import Projectile, DragModel
from services.gravity import get_gravity_at_location
import logging

LOG = logging.getLogger(__name__)

class PhysicsEngine:

    def __init__(self):
        pass

    def calculate_air_density(self, altitude_m: float, temperature_c: float = STD_TEMP_C,
                              pressure_hpa: float = STD_PRESSURE_HPA, gravity: float = GRAVITY_STD) -> float:
        """Calculates air density based on altitude and local weather.

        Uses a simplified ISA model adjusted for local temperature and pressure.

        Args:
            altitude_m: Altitude in meters.
            temperature_c: Local temperature in Celsius (at sea level equivalent).
            pressure_hpa: Local pressure in hPa (at sea level equivalent).

        Returns:
            Air density in kg/m^3.
        """
        temp_k = temperature_c + 273.15
        pressure_pa = pressure_hpa * 100.0

        # Adjust for altitude (Troposphere model)
        if altitude_m < 11000:
            temperature_at_alt = temp_k - (LAPSE_RATE * altitude_m)
            pressure_at_alt = pressure_pa * (
                (1 - (LAPSE_RATE * altitude_m) / temp_k) ** (gravity / (LAPSE_RATE * GAS_CONSTANT))
            )
        else:
            # Simplified Stratosphere (constant temp)
            temperature_at_alt = temp_k - (LAPSE_RATE * 11000)
            pressure_11k = pressure_pa * (
                (1 - (LAPSE_RATE * 11000) / temp_k) ** (gravity / (LAPSE_RATE * GAS_CONSTANT))
            )
            pressure_at_alt = pressure_11k * math.exp(
                -gravity * (altitude_m - 11000) / (GAS_CONSTANT * temperature_at_alt)
            )

        density = pressure_at_alt / (GAS_CONSTANT * temperature_at_alt)
        return max(0.0, density)

    def _calculate_speed_of_sound(self, temp_k: float) -> float:
        """Calculates speed of sound in air at a given temperature."""
        gamma = 1.4  # Adiabatic index for air
        r = GAS_CONSTANT 
        return math.sqrt(gamma * r * temp_k)

    def _get_drag_coefficient(self, mach: float, drag_model: DragModel) -> float:
        """Retrieves standard drag coefficient for the given Mach number."""
        if drag_model == DragModel.G1:
            table = G1_DRAG_TABLE
        elif drag_model == DragModel.G7:
            table = G7_DRAG_TABLE
        else:
            LOG.warning(f"Unknown drag model: {drag_model}. Defaulting to G1.")
            table = G1_DRAG_TABLE
            
        # Linear Interpolation
        for i in range(len(table) - 1):
            m_low, cd_low = table[i]
            m_high, cd_high = table[i+1]
                
            if m_low <= mach <= m_high:
                ratio = (mach - m_low) / (m_high - m_low)
                return cd_low + ratio * (cd_high - cd_low)
            
        # Out of bounds
        if mach < table[0][0]:
            return table[0][1]
        else:
            return table[-1][1]
                
        return 0.5 

    def _calculate_coriolis_acceleration(self, lat_deg: float, vx: float, vy: float, vz: float) -> Tuple[float, float, float]:
        """Calculates Coriolis acceleration vector in local ENU frame.
        
        Args:
            lat_deg: Latitude in degrees.
            vx, vy, vz: Velocity vector in m/s (East, North, Up).
            
        Returns:
            (ax, ay, az) Coriolis acceleration in m/s^2.
        """
        phi = math.radians(lat_deg)
        omega = EARTH_OMEGA

        # Earth Rotation Vector in Local ENU (East-North-Up)
        # East component is 0
        omega_y = omega * math.cos(phi) # North
        omega_z = omega * math.sin(phi) # Up
        
        # Cross Product: a_cor = -2 * (Omega x v)
        # Omega = (0, Oy, Oz)
        # v = (vx, vy, vz)
        # Cross product components:
        # x: Oy*vz - Oz*vy
        # y: Oz*vx - 0*vz
        # z: 0*vy - Oy*vx
        
        ax = -2 * (omega_y * vz - omega_z * vy)
        ay = -2 * (omega_z * vx)
        az = -2 * (-omega_y * vx)
        
        return (ax, ay, az)

    def calculate_drag_force(self, velocity_vector: Tuple[float, float, float],
                             density: float, projectile: Projectile, 
                             temp_k: float = 288.15,
                             wind_vector: Tuple[float, float, float] = (0.0, 0.0, 0.0)) -> Tuple[float, float, float]:
        """Calculates the drag force vector.

        F_drag = 0.5 * rho * v_rel^2 * Cd * A * -unit_velocity_rel

        Args:
            velocity_vector: (vx, vy, vz) in m/s (Ground Velocity).
            density: Air density in kg/m^3.
            projectile: The projectile object.
            temp_k: Local air temperature in Kelvin.
            wind_vector: (wx, wy, wz) in m/s.

        Returns:
            (fx, fy, fz) drag force vector in Newtons.
        """
        vx, vy, vz = velocity_vector
        wx, wy, wz = wind_vector
        
        # Relative Velocity = V_ground - V_wind
        rvx = vx - wx
        rvy = vy - wy
        rvz = vz - wz
        
        v_sq = rvx**2 + rvy**2 + rvz**2
        v_mag = math.sqrt(v_sq)

        if v_mag == 0:
            return (0.0, 0.0, 0.0)

        # Calculate Mach Number using Relative Speed
        sos = self._calculate_speed_of_sound(temp_k)
        mach = v_mag / sos

        # Get Standard Drag Coefficient (G1 reference)
        cd_std = self._get_drag_coefficient(mach, projectile.drag_model)
        
        # Apply Form Factor
        # Actual Cd = Cd_std * i
        cd = cd_std * projectile.form_factor

        # Drag magnitude depends on relative airspeed
        drag_mag = 0.5 * density * v_sq * cd * projectile.area_m2

        # Direction is opposite to relative velocity
        fx = -drag_mag * (rvx / v_mag)
        fy = -drag_mag * (rvy / v_mag)
        fz = -drag_mag * (rvz / v_mag)

        return (fx, fy, fz)

    def integrate_trajectory(self, start_lat: float, start_lon: float, start_alt: float,
                             velocity_vector: Tuple[float, float, float],
                             projectile: Projectile,
                             weather_data: Dict[str, Any] = None,
                             dt: float = 0.01,
                             progress_callback = None) -> Dict[str, Any]:
        """Integrates the trajectory over time."""
        
        curr_lat = start_lat
        curr_lon = start_lon
        z = start_alt
        
        # Local tangent velocity
        vx, vy, vz = velocity_vector
        t = 0.0

        total_dist = 0.0
        points = []
        telemetry = []

        # Weather defaults
        temp_c = 15.0
        pressure_hpa = 1013.25
        wind_vx, wind_vy, wind_vz = 0.0, 0.0, 0.0

        if weather_data:
            if weather_data.get("temperature"):
                 temp_c = float(weather_data["temperature"]["value"])
            if weather_data.get("pressure"):
                 pressure_hpa = float(weather_data["pressure"]["value"])
            
            # Parse Wind
            wind = weather_data.get("wind")
            if wind and wind.get("direction") and wind.get("speed"):
                try:
                    wdir = wind["direction"]
                    wspeed = float(wind["speed"])
                    wunit = wind["unit"]
                    
                    if wunit == "KT": wspeed *= 0.514444
                    elif wunit == "KMH": wspeed *= 0.277778
                    
                    if wdir != "VRB": 
                         rad_dir = float(wdir) * (math.pi / 180.0)
                         wind_vx = -wspeed * math.sin(rad_dir)
                         wind_vy = -wspeed * math.cos(rad_dir)
                except ValueError:
                    LOG.warning(f"Could not parse wind data: {wind}")

        # Loop
        step = 0
        from config.core_config import EARTH_RADIUS_M, MAX_STEPS

        while z >= 0 and step < MAX_STEPS:
 
            if progress_callback and step % 2000 == 0:
                 nominal_max = 200000
                 percent = int((step / nominal_max) * 100)
                 if percent > 99: percent = 99
                 progress_callback(percent)


            gravity = get_gravity_at_location(curr_lat, z) 
            density = self.calculate_air_density(z, temp_c, pressure_hpa, gravity)
            
            # Local Speed of Sound Temp
            sl_temp_k = temp_c + 273.15
            local_temp_k = sl_temp_k - (0.0065 * min(z, 11000))

            # Gravity acts down (-z)
            fg_z = -gravity * projectile.mass_kg

            # Drag
            fd_x, fd_y, fd_z = self.calculate_drag_force((vx, vy, vz), density, projectile, 
                                                         temp_k=local_temp_k, 
                                                         wind_vector=(wind_vx, wind_vy, wind_vz))
            
            # Coriolis (using current lat)
            ac_x, ac_y, ac_z = self._calculate_coriolis_acceleration(curr_lat, vx, vy, vz)
            fc_x = ac_x * projectile.mass_kg
            fc_y = ac_y * projectile.mass_kg
            fc_z = ac_z * projectile.mass_kg

            # Centrifugal / Geometric Lift (Curvature compensation)
            current_radius = EARTH_RADIUS_M + z
            v_horiz_sq = vx**2 + vy**2
            f_lift_z = projectile.mass_kg * v_horiz_sq / current_radius

            # Total Force
            fx = fd_x + fc_x
            fy = fd_y + fc_y
            fz = fg_z + fd_z + fc_z + f_lift_z

            # Store previous state for interpolation
            prev_lat, prev_lon, prev_z = curr_lat, curr_lon, z
            prev_vx, prev_vy, prev_vz = vx, vy, vz
            prev_t = t

            # Velocity update
            ax = fx / projectile.mass_kg
            ay = fy / projectile.mass_kg
            az = fz / projectile.mass_kg

            vx += ax * dt
            vy += ay * dt
            vz += az * dt

            # Position Update (Spherical)
            d_lat_rad = (vy / current_radius) * dt
            d_lon_rad = (vx / (current_radius * math.cos(math.radians(curr_lat)))) * dt
            
            curr_lat += math.degrees(d_lat_rad)
            curr_lon += math.degrees(d_lon_rad)
            
            z += vz * dt
            t += dt
            
            # Update Distance
            step_dist = math.sqrt( (vx*dt)**2 + (vy*dt)**2 )
            total_dist += step_dist

            # Check for ground impact
            if z < 0:
                # Interpolate exact impact
                if abs(z - prev_z) > 1e-9:
                    alpha = -prev_z / (z - prev_z)
                else:
                    alpha = 0
                
                # Back-interpolate position
                curr_lat = prev_lat + (curr_lat - prev_lat) * alpha
                curr_lon = prev_lon + (curr_lon - prev_lon) * alpha
                z = 0.0
                t = prev_t + dt * alpha
                
                # Interpolate velocity
                vx = prev_vx + (vx - prev_vx) * alpha
                vy = prev_vy + (vy - prev_vy) * alpha
                vz = prev_vz + (vz - prev_vz) * alpha
                
                points.append((curr_lat, curr_lon, z))
                
                v_horiz_impact = math.sqrt(vx**2 + vy**2)
                fpa_impact = math.degrees(math.atan2(vz, v_horiz_impact)) if v_horiz_impact > 0 else 0.0

                telemetry.append({
                    "time": round(t, 2),
                    "altitude": round(z, 2),
                    "velocity": round(math.sqrt(vx**2 + vy**2 + vz**2), 2),
                    "distance": round(total_dist, 2),
                    "flight_path_angle": round(fpa_impact, 2),
                    "latitude": curr_lat,
                    "longitude": curr_lon
                })
                break

            points.append((curr_lat, curr_lon, z))
            
            if step % 10 == 0:
                v_horiz = math.sqrt(vx**2 + vy**2)
                fpa = math.degrees(math.atan2(vz, v_horiz)) if v_horiz > 0 else 0.0
                
                telemetry.append({
                    "time": round(t, 2),
                    "altitude": round(z, 2),
                    "velocity": round(math.sqrt(vx**2 + vy**2 + vz**2), 2),
                    "distance": round(total_dist, 2),
                    "flight_path_angle": round(fpa, 2),
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
                "total_distance": round(total_dist, 2),
                "impact_velocity": round(math.sqrt(vx**2 + vy**2 + vz**2), 2),
                "drag_model": projectile.drag_model.value
            }
        }
