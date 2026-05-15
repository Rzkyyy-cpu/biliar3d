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
    [1.0, 1.0, 1.0],     # 0: Putih (Cue Ball)
    [1.0, 0.9, 0.0],     # 1: Kuning
    [0.1, 0.2, 0.9],     # 2: Biru
    [0.9, 0.1, 0.1],     # 3: Merah
    [0.5, 0.1, 0.6],     # 4: Ungu
    [1.0, 0.5, 0.0],     # 5: Oranye
    [0.1, 0.6, 0.2],     # 6: Hijau
    [0.6, 0.15, 0.15],   # 7: Maroon (Cokelat kemerahan)
    [0.05, 0.05, 0.05],  # 8: Hitam
    [1.0, 0.9, 0.0],     # 9: Kuning (Stripe)
    [0.1, 0.2, 0.9],     # 10: Biru (Stripe)
    [0.9, 0.1, 0.1],     # 11: Merah (Stripe)
    [0.5, 0.1, 0.6],     # 12: Ungu (Stripe)
    [1.0, 0.5, 0.0],     # 13: Oranye (Stripe)
    [0.1, 0.6, 0.2],     # 14: Hijau (Stripe)
    [0.6, 0.15, 0.15]    # 15: Maroon (Stripe)
]
