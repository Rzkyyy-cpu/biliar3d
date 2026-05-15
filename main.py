import glfw
from OpenGL.GL import *
import numpy as np
import time
import math
import sys

from settings import *
from math_utils import perspective, look_at, translation, rotation_axis, scale
from ball import Ball
from table import create_sphere_geometry, create_cube_geometry, create_cylinder_geometry, setup_vao
from shaders import create_shader_program

class BilliardApp:
    def __init__(self):
        if not glfw.init(): return
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3); glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        
        self.window = glfw.create_window(WINDOW_WIDTH, WINDOW_HEIGHT, "Simulasi Biliar 3D", None, None)
        if not self.window: glfw.terminate(); return
        glfw.make_context_current(self.window); glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_NORMAL)
        
        glEnable(GL_DEPTH_TEST); glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
        try: 
            self.shader = create_shader_program()
            self.loc_model = glGetUniformLocation(self.shader, "model")
            self.loc_view = glGetUniformLocation(self.shader, "view")
            self.loc_proj = glGetUniformLocation(self.shader, "projection")
            self.loc_color = glGetUniformLocation(self.shader, "objectColor")
            self.loc_light = glGetUniformLocation(self.shader, "lightPos")
            self.loc_viewpos = glGetUniformLocation(self.shader, "viewPos")
        except Exception as e: print(f"Shader Error: {e}"); sys.exit()
            
        self.sphere_v, self.sphere_i = create_sphere_geometry(BALL_RADIUS)
        self.sphere_vao = setup_vao(self.sphere_v, self.sphere_i)
        self.table_v, self.table_i = create_cube_geometry(TABLE_LENGTH/2, TABLE_HEIGHT/2, TABLE_WIDTH/2)
        self.table_vao = setup_vao(self.table_v, self.table_i)
        self.cue_v, self.cue_i = create_cylinder_geometry(0.015, 1.5)
        self.cue_vao = setup_vao(self.cue_v, self.cue_i)
        
        self.balls = []
        self.reset_game()
        self.cam_dist, self.yaw, self.pitch = 1.0, -90.0, 30.0
        self.camera_target = self.balls[0].pos.copy()
        self.update_camera_vectors()
        self.power, self.charging = 0.0, False
        self.power_dir = 1 # 1 untuk naik, -1 untuk turun
        self.ball_in_hand = True
        glfw.set_cursor_pos_callback(self.window, self.mouse_callback)

    def reset_game(self):
        self.balls = []
        self.balls.append(Ball(0, [-0.6, 0.0, 0.0], BALL_COLORS[0]))
        start_x, d, idx = 0.3, BALL_RADIUS * 2.02, 1
        for row in range(5):
            for col in range(row + 1):
                z, x = (col - row / 2.0) * d, start_x + row * (d * 0.866)
                self.balls.append(Ball(idx, [x, 0.0, z], BALL_COLORS[idx]))
                idx += 1
        self.ball_in_hand = True
        if hasattr(self, 'balls') and len(self.balls) > 0:
            self.camera_target = self.balls[0].pos.copy()

    def update_camera_vectors(self):
        ry, rp = math.radians(self.yaw), math.radians(self.pitch)
        off = np.array([self.cam_dist*math.cos(ry)*math.cos(rp), self.cam_dist*math.sin(rp), self.cam_dist*math.sin(ry)*math.cos(rp)])
        self.cam_pos = self.camera_target + off
        self.cam_front = self.camera_target - self.cam_pos
        if np.linalg.norm(self.cam_front) > 0.001: self.cam_front /= np.linalg.norm(self.cam_front)

    def mouse_callback(self, window, xpos, ypos):
        if not hasattr(self, 'last_x'): self.last_x, self.last_y = xpos, ypos
        dx, dy = (xpos - self.last_x) * 0.3, (self.last_y - ypos) * 0.3
        self.last_x, self.last_y = xpos, ypos
        if glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_LEFT) == glfw.PRESS:
            self.yaw += dx; self.pitch = np.clip(self.pitch - dy, 5.0, 85.0)
        elif glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_RIGHT) == glfw.PRESS:
            moving = any(np.linalg.norm(b.vel) > MIN_VELOCITY for b in self.balls)
            if not moving and self.balls[0].active:
                ry = math.radians(self.yaw)
                move_x = dx * 0.005 * math.sin(ry) + dy * 0.005 * math.cos(ry)
                move_z = -dx * 0.005 * math.cos(ry) + dy * 0.005 * math.sin(ry)
                self.balls[0].pos[0] = np.clip(self.balls[0].pos[0] + move_x, -TABLE_LENGTH/2 + BALL_RADIUS, TABLE_LENGTH/2 - BALL_RADIUS)
                self.balls[0].pos[2] = np.clip(self.balls[0].pos[2] + move_z, -TABLE_WIDTH/2 + BALL_RADIUS, TABLE_WIDTH/2 - BALL_RADIUS)
                self.camera_target = self.balls[0].pos.copy()

    def handle_input(self, dt):
        s = 2.0 * dt
        if glfw.get_key(self.window, glfw.KEY_W) == glfw.PRESS: self.cam_dist = max(0.2, self.cam_dist - s)
        if glfw.get_key(self.window, glfw.KEY_S) == glfw.PRESS: self.cam_dist = min(3.0, self.cam_dist + s)
        if glfw.get_key(self.window, glfw.KEY_A) == glfw.PRESS: self.yaw -= 100 * dt
        if glfw.get_key(self.window, glfw.KEY_D) == glfw.PRESS: self.yaw += 100 * dt
        
        moving = any(np.linalg.norm(b.vel) > MIN_VELOCITY for b in self.balls)
        if glfw.get_key(self.window, glfw.KEY_SPACE) == glfw.PRESS and not moving:
            # Ping-Pong Power Logic
            self.power += self.power_dir * dt * 6.0 # Kecepatan pengisian
            if self.power >= 8.0:
                self.power = 8.0
                self.power_dir = -1 # Balik arah jadi turun
            elif self.power <= 0.0:
                self.power = 0.0
                self.power_dir = 1 # Balik arah jadi naik
            self.charging = True
        elif self.charging:
            hit_dir = self.cam_front.copy(); hit_dir[1] = 0
            if np.linalg.norm(hit_dir) > 0.001: hit_dir /= np.linalg.norm(hit_dir)
            self.balls[0].vel = hit_dir * self.power * 1.5
            self.power, self.charging = 0.0, False
            self.power_dir = 1 # Reset arah ke naik untuk pukulan berikutnya
        if glfw.get_key(self.window, glfw.KEY_R) == glfw.PRESS: self.reset_game()

    def update_physics(self, dt):
        for b in self.balls: b.update(dt)
        for i, b1 in enumerate(self.balls):
            if not b1.active: continue
            bx, bz = TABLE_LENGTH/2 - BALL_RADIUS, TABLE_WIDTH/2 - BALL_RADIUS
            if abs(b1.pos[0]) > bx: b1.pos[0], b1.vel[0] = math.copysign(bx, b1.pos[0]), -b1.vel[0]*RESTITUTION
            if abs(b1.pos[2]) > bz: b1.pos[2], b1.vel[2] = math.copysign(bz, b1.pos[2]), -b1.vel[2]*RESTITUTION
            for j in range(i + 1, len(self.balls)):
                b2 = self.balls[j]
                if not b2.active: continue
                diff = b2.pos - b1.pos; dist = np.linalg.norm(diff)
                if dist < BALL_RADIUS * 2 and dist > 0:
                    n = diff/dist; vr = np.dot(b2.vel-b1.vel, n)
                    if vr < 0:
                        imp = -(1+RESTITUTION)*vr/2.0 * n
                        b1.vel, b2.vel = b1.vel-imp, b2.vel+imp
                        b1.pos, b2.pos = b1.pos - n*(BALL_RADIUS*2-dist)*0.5, b2.pos + n*(BALL_RADIUS*2-dist)*0.5
            for p in POCKET_POSITIONS:
                if np.linalg.norm(b1.pos - p) < POCKET_RADIUS:
                    if b1.id == 0:
                        b1.pos = np.array([-0.6, 0.0, 0.0]); b1.vel = np.zeros(3); self.camera_target = b1.pos.copy()
                    else:
                        b1.active, b1.vel = False, np.zeros(3)

    def run(self):
        last_t = time.time()
        while not glfw.window_should_close(self.window):
            dt = min(time.time()-last_t, 0.033); last_t = time.time()
            self.handle_input(dt); self.update_physics(dt)
            moving = any(np.linalg.norm(b.vel) > MIN_VELOCITY for b in self.balls)
            if not moving: self.camera_target = self.balls[0].pos.copy()
            self.update_camera_vectors()
            
            glClearColor(0.1, 0.1, 0.1, 1.0); glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glUseProgram(self.shader)
            
            proj = perspective(math.radians(45.0), WINDOW_WIDTH/WINDOW_HEIGHT, 0.1, 100.0)
            view = look_at(self.cam_pos, self.cam_pos + self.cam_front, [0,1,0])
            glUniformMatrix4fv(self.loc_proj, 1, GL_FALSE, proj)
            glUniformMatrix4fv(self.loc_view, 1, GL_FALSE, view)
            glUniform3fv(self.loc_light, 1, [0.0, 5.0, 2.0])
            glUniform3fv(self.loc_viewpos, 1, self.cam_pos)
            
            # 1. Render Dunia 3D
            glBindVertexArray(self.table_vao)
            glUniformMatrix4fv(self.loc_model, 1, GL_FALSE, translation(0, -TABLE_HEIGHT/2 - BALL_RADIUS, 0))
            glUniform3fv(self.loc_color, 1, [0.05, 0.35, 0.1]); glDrawElements(GL_TRIANGLES, len(self.table_i), GL_UNSIGNED_INT, None)
            
            glUniform3fv(self.loc_color, 1, [0.25, 0.12, 0.05])
            bt = 0.1
            for s in [-1, 1]:
                m = scale(1.0, 1.2, bt/(TABLE_WIDTH/2)) @ translation(0, -TABLE_HEIGHT/2 - BALL_RADIUS + 0.02, s*(TABLE_WIDTH/2 + bt/2))
                glUniformMatrix4fv(self.loc_model, 1, GL_FALSE, m); glDrawElements(GL_TRIANGLES, len(self.table_i), GL_UNSIGNED_INT, None)
                m = scale(bt/(TABLE_LENGTH/2), 1.2, 1.1) @ translation(s*(TABLE_LENGTH/2 + bt/2), -TABLE_HEIGHT/2 - BALL_RADIUS + 0.02, 0)
                glUniformMatrix4fv(self.loc_model, 1, GL_FALSE, m); glDrawElements(GL_TRIANGLES, len(self.table_i), GL_UNSIGNED_INT, None)

            glBindVertexArray(self.cue_vao); glUniform3fv(self.loc_color, 1, [0.0, 0.0, 0.0])
            for p in POCKET_POSITIONS:
                m = scale(4.2, 0.1, 4.2) @ translation(p[0], -BALL_RADIUS - 0.075, p[2])
                glUniformMatrix4fv(self.loc_model, 1, GL_FALSE, m); glDrawElements(GL_TRIANGLES, len(self.cue_i), GL_UNSIGNED_INT, None)

            glBindVertexArray(self.sphere_vao)
            for b in self.balls:
                if not b.active: continue
                m = b.rotation_matrix @ translation(b.pos[0], b.pos[1], b.pos[2])
                glUniformMatrix4fv(self.loc_model, 1, GL_FALSE, m); glUniform3fv(self.loc_color, 1, b.color); glDrawElements(GL_TRIANGLES, len(self.sphere_i), GL_UNSIGNED_INT, None)
            
            if not moving and self.balls[0].active:
                cue_ball = self.balls[0]; dir_vec = -self.cam_front.copy(); dir_vec[1] = 0
                if np.linalg.norm(dir_vec) > 0.001: dir_vec /= np.linalg.norm(dir_vec)
                angle_rad = math.radians(self.yaw)
                m_stick = rotation_axis([0, 1, 0], angle_rad) @ rotation_axis([0, 0, 1], math.pi/2) @ translation(cue_ball.pos[0] + dir_vec[0]*(0.05 + self.power*0.15), cue_ball.pos[1], cue_ball.pos[2] + dir_vec[2]*(0.05 + self.power*0.15))
                glBindVertexArray(self.cue_vao); glUniform3fv(self.loc_color, 1, [0.4, 0.2, 0.1])
                glUniformMatrix4fv(self.loc_model, 1, GL_FALSE, m_stick); glDrawElements(GL_TRIANGLES, len(self.cue_i), GL_UNSIGNED_INT, None)
            
            # 2. Render UI (Simple Green Power Bar)
            if self.charging:
                glDisable(GL_DEPTH_TEST)
                p_ratio = self.power / 8.0
                
                identity = np.eye(4, dtype=np.float32)
                glUniformMatrix4fv(self.loc_proj, 1, GL_FALSE, identity)
                glUniformMatrix4fv(self.loc_view, 1, GL_FALSE, identity)
                
                # Render Background (Hitam) - Diperbesar
                m_bg = scale(0.06, 0.9, 0.06) @ translation(0.85, 0, 0)
                glBindVertexArray(self.sphere_vao); glUniform3fv(self.loc_color, 1, [0.15, 0.15, 0.15])
                glUniformMatrix4fv(self.loc_model, 1, GL_FALSE, m_bg); glDrawElements(GL_TRIANGLES, len(self.sphere_i), GL_UNSIGNED_INT, None)
                
                # Render Power Bar (Hijau Solid) - Diperbesar
                m_bar = scale(0.05, 0.9 * p_ratio, 0.05) @ translation(0.85, -0.45 + 0.9 * p_ratio * 0.5, 0)
                glUniform3fv(self.loc_color, 1, [0.0, 1.0, 0.0])
                glUniformMatrix4fv(self.loc_model, 1, GL_FALSE, m_bar); glDrawElements(GL_TRIANGLES, len(self.sphere_i), GL_UNSIGNED_INT, None)
                
                glEnable(GL_DEPTH_TEST)
            
            glfw.swap_buffers(self.window); glfw.poll_events()
        glfw.terminate()

if __name__ == "__main__": BilliardApp().run()
