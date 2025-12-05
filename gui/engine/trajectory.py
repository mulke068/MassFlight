"""
Trajectory management for 3D points with animation support.
This module provides a Trajectory class that handles the creation,
updating, and animation of trajectories in a 3D space.
"""

from typing import List, Tuple
import math
import logging
LOG = logging.getLogger(__name__)

class Trajectory:
    def __init__(self):
        self.points: List[Tuple[float, float, float]] = []
        self.full_trajectory: List[Tuple[float, float, float]] = []
        self.current_index = 0
        self.is_animating = False
        self.animation_speed = 1  # Points per update
    
    def generate_trajectory_between_points(self, point1: Tuple[float, float, float], 
                                                 point2: Tuple[float, float, float], 
                                                 num_steps: int = 100):
        trajectory = []
        
        # Get radii of both points
        r1 = math.sqrt(point1[0]**2 + point1[1]**2 + point1[2]**2)
        r2 = math.sqrt(point2[0]**2 + point2[1]**2 + point2[2]**2)
        
        if r1 < 0.001 or r2 < 0.001:
            return []

        avg_radius = (r1 + r2) / 2

        p1_norm = tuple(c / r1 for c in point1)
        p2_norm = tuple(c / r2 for c in point2)
        
        # Calculate the points angle
        dot = sum(a * b for a, b in zip(p1_norm, p2_norm))
        dot = max(-1.0, min(1.0, dot))
        angle = math.acos(dot)

        for i in range(num_steps + 1):
            t = i / num_steps
            
            if angle < 0.001:
                point = tuple(
                    point1[j] + t * (point2[j] - point1[j]) 
                    for j in range(3)
                )
            else:
                sin_angle = math.sin(angle)
                a = math.sin((1 - t) * angle) / sin_angle
                b = math.sin(t * angle) / sin_angle
                
                point = tuple(
                    avg_radius * (a * p1_norm[j] + b * p2_norm[j])
                    for j in range(3)
                )
            
            trajectory.append(point)
        
        self.full_trajectory = trajectory
        self.reset()
    
    def set_full_trajectory(self, points: List[Tuple[float, float, float]]):
        self.full_trajectory = points.copy()
        self.reset()

    def add_point(self, x: float, y: float, z: float):
        self.points.append((x, y, z))
        self.full_trajectory.append((x, y, z))

    def get_points(self) -> List[Tuple[float, float, float]]:
        return self.points
     
    def set_animation_speed(self, speed: int):
        self.animation_speed = max(1, speed)
   
    def start_animation(self):
        self.is_animating = True
    
    def stop_animation(self):
        self.is_animating = False
 
    def update(self) -> bool:
        if not self.is_animating:
            return False
        
        if self.current_index >= len(self.full_trajectory):
            self.is_animating = False
            return False
        
        # Add point(s) based on animation speed
        for _ in range(self.animation_speed):
            if self.current_index >= len(self.full_trajectory):
                self.is_animating = False
                return False
            
            point = self.full_trajectory[self.current_index]
            self.points.append(point)
            self.current_index += 1
        
        return True
    
    def is_complete(self) -> bool:
        return self.current_index >= len(self.full_trajectory)
    
    def reset(self):
        self.points = []
        self.current_index = 0
        self.is_animating = False
   
    def clear(self):
        self.points = []
        self.full_trajectory = []
        self.current_index = 0
        self.is_animating = False
    

SAMPLE_TRAJECTORY = [
    (6.484505668236043, 7.45951639058754, 10.5188158075193054),
    (6.943539154187363, 6.993811309454366, 10.6952484720580827),
    (7.373653982754862, 6.524285767509006, 10.7501206148385438),
    (8.408566840381244, 5.060992482544663, 10.9189473110190831),
    (8.800421180232979, 3.8466121244656772, 20.7849887278803234),
    (8.59774313094928, 3.180364018965138, 30.9955096997863038),
    (7.577977449184337, 5.0944322455071855, 40.0768882589041215),
    (6.88485211120261, 6.082474067825394, 30.94997729374493),
    (6.3272110967220065, 7.002336780909118, 30.306611459522452),
    (6.416505489605292, 7.250346150793413, 20.5021866428266804),
    (6.347812825645374, 7.486555747872851, 10.9122644598915013),
    (6.425882898603122, 7.482919371428548, 10.6474060380304858),
    (6.767792420707465, 7.233201163877986, 10.3703235651074266)
]
