"""Coordinate system conversions for sphere mapping"""
import math
from math import asin, atan2, cos, sin, sqrt, pi, degrees
from config.core_config import EARTH_RADIUS_KM


def xyz_to_lonlat(x, y, z):
    """Convert 3D Cartesian coordinates to longitude/latitude"""
    radius = sqrt(x*x + y*y + z*z)
    if radius == 0:
        return 0.0, 0.0
    
    lat_ratio = max(-1.0, min(1.0, y / radius))
    lat = asin(lat_ratio) * 180 / pi
    # Use standard atan2(z, x) to produce longitude; avoid negating it
    # which caused a horizontal mirror when converting back to xyz.
    # [180,-180] to [-180,180]
    # atan2 ned for correct cal [-180, 180]
    lon = -(atan2(z, x) * 180 / pi)
    
    return lon, lat


def lonlat_to_xyz(lon, lat, radius):
    """Convert longitude/latitude to 3D Cartesian coordinates"""
    lon_rad = -(lon * pi / 180)
    lat_rad = lat * pi / 180
    
    x = radius * cos(lat_rad) * cos(lon_rad)
    y = radius * sin(lat_rad)
    z = radius * cos(lat_rad) * sin(lon_rad)
    
    return x, y, z


def ray_sphere_intersection(ray_origin, ray_dir, sphere_center, sphere_radius):
    """Calculate intersection point of ray with sphere"""
    oc = [ray_origin[i] - sphere_center[i] for i in range(3)]
    
    a = sum(ray_dir[i] * ray_dir[i] for i in range(3))
    b = 2.0 * sum(oc[i] * ray_dir[i] for i in range(3))
    c = sum(oc[i] * oc[i] for i in range(3)) - sphere_radius * sphere_radius
    
    delta = b * b - 4 * a * c
    
    if delta < 0:
        return None
    
    t1 = (-b - sqrt(delta)) / (2.0 * a)
    t2 = (-b + sqrt(delta)) / (2.0 * a)
    
    if t1 > 0:
        t = t1
    elif t2 > 0:
        t = t2
    else:
        return None
    
    intersection = [ray_origin[i] + t * ray_dir[i] for i in range(3)]
    return intersection


def calculate_bearing(lat1, lon1, lat2, lon2):
    """Calculates the initial bearing from point 1 to point 2."""
    lat1_rad = lat1 * (pi / 180)
    lat2_rad = lat2 * (pi / 180)
    d_lon_rad = (lon2 - lon1) * (pi / 180)

    y = sin(d_lon_rad) * cos(lat2_rad)
    x = cos(lat1_rad) * sin(lat2_rad) - sin(lat1_rad) * cos(lat2_rad) * cos(d_lon_rad)
    
    bearing_rad = atan2(y, x)
    bearing_deg = degrees(bearing_rad)
    
    return (bearing_deg + 360) % 360

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculates the great-circle distance between two points in km.""" 

    # https://en.wikipedia.org/wiki/Radian
    # https://en.wikipedia.org/wiki/Haversine_formula
        
    # d = r * theta
    R = EARTH_RADIUS_KM

    # degree to radian
    lat1, lon1, lat2, lon2 = [x * (pi / 180) for x in [lat1, lon1, lat2, lon2]]

    # haversine formula
    delta_phi = lat2 - lat1
    delta_lambda = lon2 - lon1

    haversine = (1 - cos(delta_phi) + cos(lat1) * cos(lat2) * (1 - cos(delta_lambda))) / 2

    theta = 2 * asin(sqrt(haversine))
    
    return R * theta
