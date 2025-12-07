from dataclasses import dataclass
from enum import Enum


class DragModel(Enum):
    """Enumeration of supported drag models."""
    G1 = "G1"
    G7 = "G7"
    # Future models can be added here (e.g., custom Cd curves)


@dataclass
class Projectile:
    """Represents a projectile with physical properties.

    Attributes:
        mass_kg: Mass of the projectile in kilograms.
        caliber_m: Diameter of the projectile in meters.
        ballistic_coefficient: Ballistic Coefficient (BC) relative to the drag model.
        drag_model: The drag model to use (default: G1).
        area_m2: Cross-sectional area in square meters (calculated if not provided).
    """
    mass_kg: float
    caliber_m: float
    ballistic_coefficient: float
    drag_model: DragModel = DragModel.G1
    area_m2: float = None
    form_factor: float = None

    def __post_init__(self):
        """Calculates derived properties after initialization."""
        if self.area_m2 is None:
            import math
            self.area_m2 = math.pi * (self.caliber_m / 2) ** 2
            
        if (self.drag_model == DragModel.G1 or self.drag_model == DragModel.G7) and self.ballistic_coefficient > 0:
            mass_lb = self.mass_kg * 2.20462
            caliber_in = self.caliber_m * 39.3701
            
            sectional_density = mass_lb / (caliber_in ** 2)
            self.form_factor = sectional_density / self.ballistic_coefficient
        else:
            self.form_factor = 1.0
