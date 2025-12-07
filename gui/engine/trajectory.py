"""Trajectory data model and management"""
from typing import List, Tuple
import math


class Trajectory:
    def __init__(self):
        self.points: List[Tuple[float, float, float]] = []
        self.full_trajectory: List[Tuple[float, float, float]] = []
        self.current_index = 0
        self.is_animating = False
        self.animation_speed = 1  # Number of points to add per update
    
    def generate_trajectory_between_points(self, point1: Tuple[float, float, float], 
                                           point2: Tuple[float, float, float], 
                                           num_steps: int = 100):
        trajectory = []
        
        # Get radii of both points
        r1 = math.sqrt(point1[0]**2 + point1[1]**2 + point1[2]**2)
        r2 = math.sqrt(point2[0]**2 + point2[1]**2 + point2[2]**2)
        
        if r1 < 0.001 or r2 < 0.001:
            return []
        
        # Use average radius for trajectory
        avg_radius = (r1 + r2) / 2
        
        # Normalize to unit sphere
        p1_norm = tuple(c / r1 for c in point1)
        p2_norm = tuple(c / r2 for c in point2)
        
        # Calculate angle between points
        dot = sum(a * b for a, b in zip(p1_norm, p2_norm))
        dot = max(-1.0, min(1.0, dot))  # Clamp for numerical stability
        angle = math.acos(dot)
        
        # Generate interpolated points using SLERP
        for i in range(num_steps + 1):
            t = i / num_steps
            
            if angle < 0.001:  # Points very close, use linear interpolation
                point = tuple(
                    point1[j] + t * (point2[j] - point1[j]) 
                    for j in range(3)
                )
            else:  # Use spherical linear interpolation (SLERP)
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
    
    def reset(self):
        self.points = []
        self.current_index = 0
        self.is_animating = False
    
    def start_animation(self):
        self.is_animating = True
    
    def stop_animation(self):
        self.is_animating = False
    
    def set_animation_speed(self, speed: int):
        self.animation_speed = max(1, speed)
    
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
    
    def clear(self):
        self.points = []
        self.full_trajectory = []
        self.current_index = 0
        self.is_animating = False
    
    def is_complete(self) -> bool:
        return self.current_index >= len(self.full_trajectory)

