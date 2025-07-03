"""Simulateur principal pour la chute libre"""

import time
from typing import List, Optional
from ..models.physics_object import PhysicsObject
from ..models.physics_engine import PhysicsEngine
from ..simulation.numerical_methods import EulerMethod, NumericalMethod
from ..utils.constants import DEFAULT_DT

class FreeFallSimulator:
    """Simulateur de chute libre avec frottement"""

    def __init__(self,
                 dt: float = DEFAULT_DT,
                 air_resistance: bool = True,
                 ground_level: float = 0.0,
                 air_density_factor: float = 1.0,
                 numerical_method: Optional[NumericalMethod] = None):
        """
        Initialise le simulateur

        Args:
            dt: Pas de temps
            air_resistance: Active la résistance de l'air
            ground_level: Hauteur du sol
            air_density_factor: Facteur de densité de l'air (1.0 = normal)
            numerical_method: Méthode numérique à utiliser
        """
        self.dt = dt
        self.physics_engine = PhysicsEngine(air_resistance, ground_level, air_density_factor)
        self.numerical_method = numerical_method or EulerMethod()
        self.objects: List[PhysicsObject] = []
        self.time = 0.0
        self.running = False
        self.paused = False

    def set_air_density_factor(self, factor: float):
        """Modifie le facteur de densité de l'air"""
        self.physics_engine.set_air_density_factor(factor)

    def get_air_density_factor(self) -> float:
        """Retourne le facteur de densité de l'air actuel"""
        return self.physics_engine.air_density_factor

    def add_object(self, obj: PhysicsObject):
        """Ajoute un objet à la simulation"""
        self.objects.append(obj)

    def remove_object(self, obj: PhysicsObject):
        """Retire un objet de la simulation"""
        if obj in self.objects:
            self.objects.remove(obj)

    def reset(self):
        """Remet la simulation à zéro"""
        self.time = 0.0
        for obj in self.objects:
            obj.reset_history()

    def step(self):
        """Effectue un pas de simulation"""
        if not self.paused:
            for obj in self.objects:
                # Mise à jour de la physique
                collision, peak_height = self.physics_engine.update_object(obj, self.dt, self.numerical_method)

                # Mise à jour de l'historique
                obj.update_history(self.time, self.physics_engine.ground_level)

            self.time += self.dt

    def run_for_duration(self, duration: float):
        """Exécute la simulation pendant une durée donnée"""
        end_time = self.time + duration
        while self.time < end_time:
            self.step()

    def start(self):
        """Démarre la simulation"""
        self.running = True
        self.paused = False

    def pause(self):
        """Met en pause la simulation"""
        self.paused = not self.paused

    def stop(self):
        """Arrête la simulation"""
        self.running = False
        self.paused = False

    def get_objects_info(self) -> List[dict]:
        """Retourne les informations des objets pour l'affichage"""
        info = []
        for obj in self.objects:
            info.append({
                'x': obj.x,
                'y': obj.y,
                'vx': obj.vx,
                'vy': obj.vy,
                'radius': obj.radius,
                'color': obj.color,
                'speed': obj.speed,
                'kinetic_energy': obj.kinetic_energy,
                'potential_energy': obj.potential_energy(self.physics_engine.ground_level)
            })
        return info

    def get_simulation_info(self) -> dict:
        """Retourne les informations générales de la simulation"""
        return {
            'time': self.time,
            'paused': self.paused,
            'air_resistance': self.physics_engine.air_resistance,
            'air_density_factor': self.physics_engine.air_density_factor,
            'ground_level': self.physics_engine.ground_level
        }