import numpy as np

# --- Window Settings ---
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

# --- Konstanta Fisika ---
BALL_RADIUS = 0.0286
BALL_MASS = 0.17
FRICTION_COEFF = 0.97  # Sedikit lebih licin
RESTITUTION = 0.95
MIN_VELOCITY = 0.05    # Lebih tinggi = lebih cepat dianggap diam

TABLE_WIDTH = 1.12
TABLE_LENGTH = 2.24
TABLE_HEIGHT = 0.05

POCKET_RADIUS = 0.08
POCKET_POSITIONS = [
    np.array([-TABLE_LENGTH/2, 0.0, -TABLE_WIDTH/2]),
    np.array([0.0, 0.0, -TABLE_WIDTH/2]),
    np.array([TABLE_LENGTH/2, 0.0, -TABLE_WIDTH/2]),
    np.array([-TABLE_LENGTH/2, 0.0, TABLE_WIDTH/2]),
    np.array([0.0, 0.0, TABLE_WIDTH/2]),
    np.array([TABLE_LENGTH/2, 0.0, TABLE_WIDTH/2]),
]

BALL_COLORS = [
    [1.0, 1.0, 1.0], [1.0, 0.85, 0.0], [0.1, 0.2, 0.8], [0.8, 0.1, 0.1],
    [0.5, 0.1, 0.6], [1.0, 0.4, 0.0], [0.1, 0.5, 0.1], [0.6, 0.1, 0.1],
    [0.05, 0.05, 0.05], [1.0, 0.85, 0.0], [0.1, 0.2, 0.8], [0.8, 0.1, 0.1],
    [0.5, 0.1, 0.6], [1.0, 0.4, 0.0], [0.1, 0.5, 0.1], [0.6, 0.1, 0.1]
]
