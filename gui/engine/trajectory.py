"""Trajectory data model and management"""
from typing import List, Tuple


class Trajectory:
    """Manages trajectory points and animation"""
    
    def __init__(self):
        self.points: List[Tuple[float, float, float]] = []
        self.full_trajectory: List[Tuple[float, float, float]] = []
        self.current_index = 0
        self.is_animating = False
    
    def set_full_trajectory(self, points: List[Tuple[float, float, float]]):
        """Set the complete trajectory data"""
        self.full_trajectory = points.copy()
        self.reset()
    
    def reset(self):
        """Reset animation to beginning"""
        self.points = []
        self.current_index = 0
        self.is_animating = False
    
    def start_animation(self):
        """Start trajectory animation"""
        self.is_animating = True
    
    def stop_animation(self):
        """Stop trajectory animation"""
        self.is_animating = False
    
    def update(self) -> bool:
        """Update animation by one frame"""
        if not self.is_animating:
            return False
        
        if self.current_index >= len(self.full_trajectory):
            self.is_animating = False
            return False
        
        point = self.full_trajectory[self.current_index]
        self.points.append(point)
        self.current_index += 1
        
        return True
    
    def get_points(self) -> List[Tuple[float, float, float]]:
        """Get current visible trajectory points"""
        return self.points
    
    def add_point(self, x: float, y: float, z: float):
        """Add a single point to the trajectory"""
        self.points.append((x, y, z))
        self.full_trajectory.append((x, y, z))
    
    def clear(self):
        """Clear all trajectory data"""
        self.points = []
        self.full_trajectory = []
        self.current_index = 0
        self.is_animating = False
    
    def is_complete(self) -> bool:
        """Check if animation is complete"""
        return self.current_index >= len(self.full_trajectory)


SAMPLE_TRAJECTORY = [
    (6.484505668236043, 7.45951639058754, 1.5188158075193054),
    (6.943539154187363, 6.993811309454366, 1.6952484720580827),
    (7.373653982754862, 6.524285767509006, 1.7501206148385438),
    (8.408566840381244, 5.060992482544663, 1.9189473110190831),
    (8.800421180232979, 3.8466121244656772, 2.7849887278803234),
    (8.59774313094928, 3.180364018965138, 3.9955096997863038),
    (7.577977449184337, 5.0944322455071855, 4.0768882589041215),
    (6.88485211120261, 6.082474067825394, 3.94997729374493),
    (6.3272110967220065, 7.002336780909118, 3.306611459522452),
    (6.416505489605292, 7.250346150793413, 2.5021866428266804),
    (6.347812825645374, 7.486555747872851, 1.9122644598915013),
    (6.425882898603122, 7.482919371428548, 1.6474060380304858),
    (6.767792420707465, 7.233201163877986, 1.3703235651074266)
]
