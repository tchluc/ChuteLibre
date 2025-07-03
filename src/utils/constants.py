"""Constantes physiques et paramètres de simulation"""

# Constantes physiques
GRAVITY = 9.81  # m/s²
AIR_DENSITY = 1.225  # kg/m³

# Paramètres de simulation
DEFAULT_DT = 0.001  # pas de temps par défaut (s)
DEFAULT_WIDTH = 800
DEFAULT_HEIGHT = 600

# Couleurs pour pygame
COLORS = {
    'BLACK': (0, 0, 0),
    'WHITE': (255, 255, 255),
    'RED': (255, 0, 0),
    'BLUE': (0, 0, 255),
    'GREEN': (0, 255, 0),
    'GRAY': (128, 128, 128)
}

# Coefficients de traînée typiques
DRAG_COEFFICIENTS = {
    'sphere': 0.47,
    'cube': 1.05,
    'cylinder': 0.82,
    'streamlined': 0.04
}

# Constantes de l'interface
FPS = 80
SCREEN_WIDTH = 1500
SCREEN_HEIGHT = 900
BALL_RADIUS = 12
SCALE = 60  # pixels par mètre

# Configuration des objets prédéfinis
BALL_TYPES = [
    {"name": "Tennis", "mass": 0.058, "radius": 0.033, "drag_coefficient": 0.508, "color": "ball1"},
    {"name": "Golf", "mass": 0.046, "radius": 0.021, "drag_coefficient": 0.24, "color": "ball2"},
    {"name": "Basketball", "mass": 0.624, "radius": 0.12, "drag_coefficient": 0.47, "color": "warning"},
    {"name": "Plume", "mass": 0.001, "radius": 0.05, "drag_coefficient": 0.6, "color": "secondary"}
]

GROUND_TYPES = [
    {"name": "Béton", "restitution": 0.85},
    {"name": "Parquet", "restitution": 0.90},
    {"name": "Gazon", "restitution": 0.65},
    {"name": "Sable", "restitution": 0.30},
    {"name": "Caoutchouc", "restitution": 0.95}
]

# Facteurs de densité de l'air
AIR_DENSITY_FACTORS = [
    {"name": "Vide spatial (0.0x)", "factor": 0.001},
    {"name": "Très raréfié (0.2x)", "factor": 0.2},
    {"name": "Air normal (1.0x)", "factor": 1.0},
    {"name": "Air humide (1.3x)", "factor": 1.3},
    {"name": "Air très dense (3.0x)", "factor": 3.0}
]

INITIAL_HEIGHTS = [3.0, 5.0, 8.0, 10.0, 15.0, 20.0]