"""Coordinate system conversions for sphere mapping"""
import math
from math import asin, atan2, cos, sin, sqrt, pi


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
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    d_lon_rad = math.radians(lon2 - lon1)

    y = math.sin(d_lon_rad) * math.cos(lat2_rad)
    x = math.cos(lat1_rad) * math.sin(lat2_rad) - \
        math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(d_lon_rad)
    
    bearing_rad = math.atan2(y, x)
    bearing_deg = math.degrees(bearing_rad)
    
    return (bearing_deg + 360) % 360

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculates the great-circle distance between two points in km."""
    R = 6371.0 # Earth radius in km
    
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    
    a = math.sin(d_lat / 2)**2 + \
        math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * \
        math.sin(d_lon / 2)**2
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c
