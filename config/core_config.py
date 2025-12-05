"""Core configuration for MassFlight.

This module consolidates physics and simulation constants.
"""

# Physics Constants (ISA & WGS84)
STD_TEMP_K = 288.15
STD_PRESSURE_PA = 101325.0
LAPSE_RATE = 0.0065  # K/m
GAS_CONSTANT = 287.05
GRAVITY_STD = 9.80665

# Earth Constants
EARTH_RADIUS_KM = 6371.0
EARTH_RADIUS_M = EARTH_RADIUS_KM * 1000.0

# Simulation Configuration
MAX_VELOCITY = 50000.0
MAX_STEPS = 100000
DT_DEFAULT = 0.01

# Tolerance for firing solution
HEADING_TOLERANCE_DEG = 0.001
RANGE_TOLERANCE_M = 50.0

# Solver constraints
MAX_SOLVER_ITERATIONS_HEADING = 50
MAX_SOLVER_ITERATIONS_VELOCITY = 15
