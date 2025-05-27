import pygame

# Constantes physiques
g = 9.81  # Accélération gravitationnelle (m/s²)

# Constantes de simulation
FPS = 60
dt = 1.0 / FPS
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
BALL_RADIUS = 10
GROUND_Y = SCREEN_HEIGHT - 150
SCALE = 50  # Conversion m -> pixels (1 m = 50 pixels)

# Couleurs modernes
COLORS = {
    'primary': (70, 130, 180),
    'primary_hover': (100, 149, 237),
    'secondary': (60, 179, 113),
    'secondary_hover': (85, 195, 135),
    'danger': (220, 53, 69),
    'danger_hover': (225, 75, 85),
    'warning': (255, 193, 7),
    'warning_hover': (255, 210, 50),
    'background': (248, 249, 250),
    'card': (255, 255, 255),
    'text': (52, 58, 64),
    'text_light': (108, 117, 125),
    'border': (206, 212, 218),
    'shadow': (0, 0, 0, 30),
    'ball1': (220, 53, 69),
    'ball2': (0, 123, 255),
    'grid': (230, 234, 238)
}

# Options pour les paramètres
ball_types = [
    {"name": "Tennis", "m": 0.058, "k": 0.015},  # Léger, plus de frottement
    {"name": "Golf", "m": 0.046, "k": 0.01},
    {"name": "Bowling", "m": 7.0, "k": 0.005}   # Lourd, moins de frottement
]

ground_types = [
    {"name": "Béton", "e": 0.9},  # Rebond élevé
    {"name": "Gazon", "e": 0.7},
    {"name": "Sable", "e": 0.4}   # Rebond faible
]

wind_speeds = [0.0, 5.0, 10.0]  # m/s
heights = [5.0, 10.0, 15.0]     # m