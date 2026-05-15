import numpy as np
import math

def perspective(fov, aspect, near, far):
    f = 1.0 / math.tan(fov / 2.0)
    # Standard Perspective Matrix (Row-Major)
    return np.array([
        [f / aspect, 0, 0, 0],
        [0, f, 0, 0],
        [0, 0, (far + near) / (near - far), (2 * far * near) / (near - far)],
        [0, 0, -1, 0]
    ], dtype=np.float32)

def look_at(eye, target, up):
    zaxis = (eye - target)
    zaxis /= np.linalg.norm(zaxis)
    xaxis = np.cross(up, zaxis)
    xaxis /= np.linalg.norm(xaxis)
    yaxis = np.cross(zaxis, xaxis)
    
    # View Matrix (Row-Major)
    res = np.eye(4, dtype=np.float32)
    res[0, :3] = xaxis
    res[1, :3] = yaxis
    res[2, :3] = zaxis
    res[0, 3] = -np.dot(xaxis, eye)
    res[1, 3] = -np.dot(yaxis, eye)
    res[2, 3] = -np.dot(zaxis, eye)
    return res

def translation(x, y, z):
    res = np.eye(4, dtype=np.float32)
    res[0, 3], res[1, 3], res[2, 3] = x, y, z
    return res

def rotation_axis(axis, angle):
    c, s = math.cos(angle), math.sin(angle)
    t = 1 - c
    norm = np.linalg.norm(axis)
    if norm < 0.0001: return np.eye(4, dtype=np.float32)
    x, y, z = axis / norm
    # Rotation Matrix (Row-Major)
    return np.array([
        [t*x*x+c,   t*x*y-s*z, t*x*z+s*y, 0],
        [t*x*y+s*z, t*y*y+c,   t*y*z-s*x, 0],
        [t*x*z-s*y, t*y*z+s*x, t*z*z+c,   0],
        [0,         0,         0,         1]
    ], dtype=np.float32)

def scale(sx, sy, sz):
    res = np.eye(4, dtype=np.float32)
    res[0, 0], res[1, 1], res[2, 2] = sx, sy, sz
    return res
