import numpy as np
import math
from settings import *
from math_utils import rotation_axis

class Ball:
    def __init__(self, id, pos, color):
        self.id = id
        self.pos = np.array(pos, dtype=np.float32)
        self.vel = np.zeros(3, dtype=np.float32)
        self.color = np.array(color, dtype=np.float32)
        self.radius = BALL_RADIUS
        self.mass = BALL_MASS
        self.active = True
        self.rotation_matrix = np.eye(4, dtype=np.float32)

    def update(self, dt):
        if not self.active: return
        self.pos += self.vel * dt
        
        speed = np.linalg.norm(self.vel)
        if speed > 0.001:
            axis = np.cross([0, 1, 0], self.vel)
            if np.linalg.norm(axis) > 0.0001:
                angle = (speed * dt) / self.radius
                rot = rotation_axis(axis, angle)
                # Column-Major accumulation: New * Old
                self.rotation_matrix = rot @ self.rotation_matrix

        self.vel *= FRICTION_COEFF ** dt
        speed = np.linalg.norm(self.vel)
        if speed > 0:
            deceleration = 0.38 * dt 
            new_speed = max(0, speed - deceleration)
            self.vel = (self.vel / speed) * new_speed
        if speed < MIN_VELOCITY:
            self.vel = np.zeros(3)
