import math
import numpy as np
from OpenGL.GL import *
from table import create_cylinder_geometry, setup_vao
from math_utils import translation, rotation_axis

class Cue:
    def __init__(self):
        # Geometri silinder untuk stik biliar
        self.v, self.i = create_cylinder_geometry(0.015, 1.5)
        self.vao = setup_vao(self.v, self.i)
        self.color = [0.4, 0.2, 0.1]
        
        # State kekuatan pukulan (power)
        self.power = 0.0
        self.charging = False
        self.power_dir = 1

    def charge(self, dt):
        """Mengisi power pukulan sistem ping-pong."""
        self.power += self.power_dir * dt * 6.0
        if self.power >= 8.0:
            self.power = 8.0
            self.power_dir = -1
        elif self.power <= 0.0:
            self.power = 0.0
            self.power_dir = 1
        self.charging = True

    def release(self):
        """Melepaskan pukulan, mengembalikan nilai power saat ini, dan mereset status."""
        power_released = self.power
        self.power = 0.0
        self.charging = False
        self.power_dir = 1
        return power_released

    def render(self, loc_model, loc_color, cue_ball_pos, cam_front, yaw=0):
        """Merender stik biliar dengan posisi menyesuaikan posisi bola, arah kamera (termasuk pitch), dan power."""
        D_original = -cam_front.copy()
        if np.linalg.norm(D_original) > 0.001:
            D_original /= np.linalg.norm(D_original)
            
        UP = np.array([0.0, 1.0, 0.0], dtype=np.float32)
        
        # Terapkan tilt (kemiringan) agar bagian belakang stik sedikit lebih rendah
        right_vec = np.cross(UP, D_original)
        if np.linalg.norm(right_vec) < 0.001:
            right_vec = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        else:
            right_vec /= np.linalg.norm(right_vec)
            
        down_vec = np.cross(right_vec, D_original)
        down_vec /= np.linalg.norm(down_vec)
        
        tilt_angle = math.radians(5) # 5 derajat kemiringan ke bawah
        D_tilted = D_original * math.cos(tilt_angle) + down_vec * math.sin(tilt_angle)
        D_tilted /= np.linalg.norm(D_tilted)
        
        # Matriks rotasi menggunakan basis ortogonal dari D_tilted
        new_X = np.cross(UP, D_tilted)
        if np.linalg.norm(new_X) < 0.001:
            new_X = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        else:
            new_X /= np.linalg.norm(new_X)
            
        new_Z = np.cross(new_X, D_tilted)
        new_Z /= np.linalg.norm(new_Z)
        
        R_python = np.array([
            [new_X[0], new_X[1], new_X[2], 0],
            [D_tilted[0], D_tilted[1], D_tilted[2], 0],
            [new_Z[0], new_Z[1], new_Z[2], 0],
            [0,        0,        0,        1]
        ], dtype=np.float32)
        
        # Jarak tambahan stik ditarik mundur (berdasarkan power)
        offset_dist = 0.2 + self.power * 0.15
        
        # Posisi ujung stik tetap berada pada garis pandang kamera asli (D_original)
        m_stick = R_python @ translation(
            cue_ball_pos[0] + D_original[0] * offset_dist, 
            cue_ball_pos[1] + D_original[1] * offset_dist, 
            cue_ball_pos[2] + D_original[2] * offset_dist
        )
        
        glBindVertexArray(self.vao)
        glUniform3fv(loc_color, 1, self.color)
        glUniformMatrix4fv(loc_model, 1, GL_FALSE, m_stick)
        glDrawElements(GL_TRIANGLES, len(self.i), GL_UNSIGNED_INT, None)
