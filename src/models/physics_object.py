"""Classe représentant un objet physique en chute libre"""

import math
from src.utils.constants import DRAG_COEFFICIENTS
from ..utils.constants import GRAVITY

class PhysicsObject:
    """Objet physique avec propriétés pour la simulation de chute libre"""

    def __init__(self,
                 x: float = 0.0,
                 y: float = 0.0,
                 vx: float = 0.0,
                 vy: float = 0.0,
                 mass: float = 1.0,
                 radius: float = 0.1,
                 drag_coefficient: float = DRAG_COEFFICIENTS['sphere'],
                 restitution_coefficient: float = 0.8,
                 color: str = 'BLUE'):
        """
        Initialise un objet physique

        Args:
            x, y: Position initiale (m)
            vx, vy: Vitesse initiale (m/s)
            mass: Masse (kg)
            radius: Rayon (m)
            drag_coefficient: Coefficient de traînée
            restitution_coefficient: Coefficient de restitution (0-1)
            color: Couleur pour l'affichage
        """
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.mass = mass
        self.radius = radius
        self.drag_coefficient = drag_coefficient
        self.restitution_coefficient = restitution_coefficient
        self.color = color

        # Historique pour les graphiques
        self.history = {
            'time': [],
            'x': [],
            'y': [],
            'vx': [],
            'vy': [],
            'kinetic_energy': [],
            'potential_energy': []
        }

    @property
    def area(self) -> float:
        """Aire de la section transversale"""
        return math.pi * self.radius ** 2

    @property
    def speed(self) -> float:
        """Vitesse instantanée"""
        return math.sqrt(self.vx ** 2 + self.vy ** 2)

    @property
    def kinetic_energy(self) -> float:
        """Énergie cinétique"""
        return 0.5 * self.mass * self.speed ** 2

    def potential_energy(self, reference_height: float = 0.0) -> float:
        """Énergie potentielle"""

        return self.mass * GRAVITY * (self.y - reference_height)

    def update_history(self, time: float, reference_height: float = 0.0):
        """Met à jour l'historique des données"""
        self.history['time'].append(time)
        self.history['x'].append(self.x)
        self.history['y'].append(self.y)
        self.history['vx'].append(self.vx)
        self.history['vy'].append(self.vy)
        self.history['kinetic_energy'].append(self.kinetic_energy)
        self.history['potential_energy'].append(self.potential_energy(reference_height))

    def reset_history(self):
        """Remet à zéro l'historique"""
        for key in self.history:
            self.history[key].clear()

    def __str__(self) -> str:
        return f"PhysicsObject(pos=({self.x:.2f}, {self.y:.2f}), " \
               f"vel=({self.vx:.2f}, {self.vy:.2f}), mass={self.mass:.2f})"