
from math import e, pi, sin, sqrt


def get_gravity_at_location(lat , altitude_meters= 0) -> float:
    """
    Calculates local gravity (m/s^2) using WGS84 Somigliana equation 
    minus the Free Air Correction for altitude.

    Args:
        lat: Latitude in decimal degrees.
        altitude_meters: Altitude above sea level in meters.

    Returns:
        float: Gravity in m/s^2
    """
    # WGS84 Ellipsoidal Gravity Formula
    #$$ \gamma (\phi )=\gamma _{a}\frac{1+p\cdot \sin ^{2}\phi }{\sqrt{1-e^{2}\cdot \sin ^{2}\phi }}\ $$
    
    
    g_equator = 9.7803253359
    
    # WGS84 formula constant
    k = 0.00193185265241
    
    # square of eccentricity
    e2 = 0.00669437999014
    
    ## convert to radian 
    sin_sq_lat = sin(lat * (pi / 180)) ** 2
    
    # calculate graivity on surface of the ellipsoid
    g_surface = g_equator * (1 + k * sin_sq_lat) / sqrt(1 - e2 * sin_sq_lat)
    
    # apply air correction
    # 3.086e-6 m/s^2 per meter aprx
    air_correction = 3.086e-6 * altitude_meters

    return g_surface - air_correction