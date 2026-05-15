import numpy as np
import math

def perspective(fov, aspect, near, far):
    f = 1.0 / math.tan(fov / 2.0)
    # Murni Column-Major (OpenGL Standard)
    # Linear: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    return np.array([
        [f / aspect, 0, 0, 0],
        [0, f, 0, 0],
        [0, 0, (far + near) / (near - far), -1],
        [0, 0, (2 * far * near) / (near - far), 0]
    ], dtype=np.float32)

def look_at(eye, target, up):
    z = (eye - target)
    z /= np.linalg.norm(z)
    x = np.cross(up, z)
    x /= np.linalg.norm(x)
    y = np.cross(z, x)
    
    # Murni Column-Major View Matrix
    res = np.eye(4, dtype=np.float32)
    res[0, 0], res[1, 0], res[2, 0] = x[0], x[1], x[2]
    res[0, 1], res[1, 1], res[2, 1] = y[0], y[1], y[2]
    res[0, 2], res[1, 2], res[2, 2] = z[0], z[1], z[2]
    res[3, 0] = -np.dot(x, eye)
    res[3, 1] = -np.dot(y, eye)
    res[3, 2] = -np.dot(z, eye)
    return res

def translation(x, y, z):
    res = np.eye(4, dtype=np.float32)
    # Translation in the last COLUMN (for OpenGL)
    # In NumPy [row, col], Column 3 is [0,3], [1,3], [2,3]
    # BUT we want linear index 12, 13, 14. 
    # In NumPy default, linear index 12 is [3, 0].
    res[3, 0], res[3, 1], res[3, 2] = x, y, z
    return res

def rotation_axis(axis, angle):
    c, s = math.cos(angle), math.sin(angle)
    t = 1 - c
    norm = np.linalg.norm(axis)
    if norm < 0.0001: return np.eye(4, dtype=np.float32)
    x, y, z = axis / norm
    # Column-Major Rotation (Transpose of Row-Major)
    return np.array([
        [t*x*x+c,   t*x*y+s*z, t*x*z-s*y, 0],
        [t*x*y-s*z, t*y*y+c,   t*y*z+s*x, 0],
        [t*x*z+s*y, t*y*z-s*x, t*z*z+c,   0],
        [0,         0,         0,         1]
    ], dtype=np.float32)

def scale(sx, sy, sz):
    res = np.eye(4, dtype=np.float32)
    res[0, 0], res[1, 1], res[2, 2] = sx, sy, sz
    return res
