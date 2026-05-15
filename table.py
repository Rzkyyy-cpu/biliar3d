import numpy as np
import math
from OpenGL.GL import *
import ctypes

def create_sphere_geometry(radius, segments=32):
    vertices = []
    indices = []
    for i in range(segments + 1):
        lat = math.pi * i / segments
        for j in range(segments + 1):
            lon = 2 * math.pi * j / segments
            x = math.cos(lon) * math.sin(lat)
            y = math.cos(lat)
            z = math.sin(lon) * math.sin(lat)
            # Pos (x,y,z) + Normal (x,y,z)
            vertices.extend([x * radius, y * radius, z * radius, x, y, z])
            
    for i in range(segments):
        for j in range(segments):
            first = i * (segments + 1) + j
            second = first + segments + 1
            indices.extend([first, second, first + 1, second, second + 1, first + 1])
            
    return np.array(vertices, dtype=np.float32), np.array(indices, dtype=np.uint32)

def create_cube_geometry(w, h, d):
    # Format: Pos (3) + Normal (3)
    vertices = [
        # Front
        -w, -h,  d,  0, 0,  1,   w, -h,  d,  0, 0,  1,   w,  h,  d,  0, 0,  1,  -w,  h,  d,  0, 0,  1,
        # Back
        -w, -h, -d,  0, 0, -1,   w, -h, -d,  0, 0, -1,   w,  h, -d,  0, 0, -1,  -w,  h, -d,  0, 0, -1,
        # Top
        -w,  h, -d,  0, 1,  0,   w,  h, -d,  0, 1,  0,   w,  h,  d,  0, 1,  0,  -w,  h,  d,  0, 1,  0,
        # Bottom
        -w, -h, -d,  0,-1,  0,   w, -h, -d,  0,-1,  0,   w, -h,  d,  0,-1,  0,  -w, -h,  d,  0,-1,  0,
        # Left
        -w, -h, -d, -1, 0,  0,  -w, -h,  d, -1, 0,  0,  -w,  h,  d, -1, 0,  0,  -w,  h, -d, -1, 0,  0,
        # Right
         w, -h, -d,  1, 0,  0,   w, -h,  d,  1, 0,  0,   w,  h,  d,  1, 0,  0,   w,  h, -d,  1, 0,  0,
    ]
    indices = []
    for i in range(6):
        base = i * 4
        indices.extend([base, base + 1, base + 2, base, base + 2, base + 3])
    return np.array(vertices, dtype=np.float32), np.array(indices, dtype=np.uint32)

def create_cylinder_geometry(radius, length, segments=16):
    vertices = []
    indices = []
    # Body
    for i in range(segments + 1):
        theta = 2.0 * math.pi * i / segments
        x, z = math.cos(theta), math.sin(theta)
        # Bottom ring
        vertices.extend([x * radius, 0, z * radius, x, 0, z])
        # Top ring
        vertices.extend([x * radius, length, z * radius, x, 0, z])
        
    for i in range(segments):
        b1, t1 = i * 2, i * 2 + 1
        b2, t2 = (i + 1) * 2, (i + 1) * 2 + 1
        indices.extend([b1, t1, b2, t1, t2, b2])
        
    return np.array(vertices, dtype=np.float32), np.array(indices, dtype=np.uint32)

def setup_vao(vertices, indices):
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)
    
    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
    
    ebo = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)
    
    # Position
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)
    # Normal
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))
    glEnableVertexAttribArray(1)
    
    glBindVertexArray(0)
    return vao
