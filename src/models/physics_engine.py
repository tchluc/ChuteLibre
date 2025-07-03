"""Moteur physique pour calculer les forces et accélérations"""

import math
from typing import Tuple
from .physics_object import PhysicsObject
from ..utils.constants import GRAVITY, AIR_DENSITY

class PhysicsEngine:
    """Moteur physique pour la simulation de chute libre avec frottement"""

    def __init__(self, air_resistance: bool = True, ground_level: float = 0.0, air_density_factor: float = 1.0):
        """
        Initialise le moteur physique

        Args:
            air_resistance: Active/désactive la résistance de l'air
            ground_level: Hauteur du sol
            air_density_factor: Facteur multiplicateur pour la densité de l'air (1.0 = normal, 2.0 = air dense)
        """
        self.air_resistance = air_resistance
        self.ground_level = ground_level
        self.air_density_factor = air_density_factor
        self.total_rebounds = 0
        self.simulation_stopped = False
        self.stop_threshold_speed = 0.05  # m/s - vitesse en dessous de laquelle on considère l'arrêt
        self.stop_threshold_height = 0.01  # m - hauteur en dessous de laquelle on considère l'arrêt

        # Variables pour suivre la hauteur maximale après chaque rebond
        self.just_bounced = False
        self.max_height_after_bounce = 0.0
        self.previous_y = 0.0
        self.ascending = False

    @property
    def effective_air_density(self) -> float:
        """Densité effective de l'air selon le facteur"""
        return AIR_DENSITY * self.air_density_factor

    def calculate_forces(self, obj: PhysicsObject) -> Tuple[float, float]:
        """
        Calcule les forces appliquées à l'objet

        Returns:
            (force_x, force_y) en Newtons
        """
        # Force gravitationnelle
        force_gravity_x = 0.0
        force_gravity_y = -obj.mass * GRAVITY

        # Force de frottement de l'air
        force_drag_x = 0.0
        force_drag_y = 0.0

        if self.air_resistance and obj.speed > 0:
            # F_drag = 0.5 * ρ * Cd * A * v²
            drag_magnitude = 0.5 * self.effective_air_density * obj.drag_coefficient * obj.area * obj.speed ** 2

            # Direction opposée à la vitesse
            force_drag_x = -drag_magnitude * obj.vx / obj.speed
            force_drag_y = -drag_magnitude * obj.vy / obj.speed

        total_force_x = force_gravity_x + force_drag_x
        total_force_y = force_gravity_y + force_drag_y

        return total_force_x, total_force_y

    def set_air_density_factor(self, factor: float):
        """
        Modifie le facteur de densité de l'air

        Args:
            factor: Facteur multiplicateur (1.0 = normal, 0.5 = air raréfié, 2.0 = air dense)
        """
        self.air_density_factor = max(0.1, min(10.0, factor))  # Limiter entre 0.1x et 10x

    def calculate_derivatives(self, x: float, y: float, vx: float, vy: float, obj: PhysicsObject) -> Tuple[float, float, float, float]:
        """
        Calcule les dérivées pour l'intégration numérique

        Returns:
            (dx/dt, dy/dt, dvx/dt, dvy/dt)
        """
        # Mise à jour temporaire de la position/vitesse pour le calcul des forces
        old_x, old_y, old_vx, old_vy = obj.x, obj.y, obj.vx, obj.vy
        obj.x, obj.y, obj.vx, obj.vy = x, y, vx, vy

        # Calcul des forces
        force_x, force_y = self.calculate_forces(obj)

        # Restauration de l'état original
        obj.x, obj.y, obj.vx, obj.vy = old_x, old_y, old_vx, old_vy

        # Dérivées
        dx_dt = vx
        dy_dt = vy
        dvx_dt = force_x / obj.mass
        dvy_dt = force_y / obj.mass

        return dx_dt, dy_dt, dvx_dt, dvy_dt

    def handle_ground_collision(self, obj: PhysicsObject) -> bool:
        """
        Gère la collision avec le sol

        Returns:
            True si collision détectée
        """
        if obj.y - obj.radius <= self.ground_level and obj.vy < 0:
            # Repositionner l'objet au-dessus du sol
            obj.y = self.ground_level + obj.radius

            # Calculer la vitesse après rebond
            new_vy = -obj.vy * obj.restitution_coefficient
            new_vx = obj.vx * obj.restitution_coefficient  # Réduction de la vitesse horizontale

            # Vérifier si le rebond est significatif
            if abs(new_vy) > self.stop_threshold_speed:
                obj.vy = new_vy
                obj.vx = new_vx
                self.total_rebounds += 1

                # Marquer qu'il vient de rebondir
                self.just_bounced = True
                self.max_height_after_bounce = obj.y
                self.ascending = True

                return True
            else:
                # Arrêter la balle si le rebond est trop faible
                obj.vy = 0
                obj.vx = 0
                obj.y = self.ground_level + obj.radius
                self.simulation_stopped = True
                return True

        return False

    def track_max_height(self, obj: PhysicsObject) -> float:
        """
        Suit la hauteur maximale après un rebond

        Returns:
            Hauteur maximale atteinte si on vient de passer le pic, sinon 0
        """
        if not self.just_bounced:
            return 0.0

        # Vérifier si on monte ou on descend
        if self.ascending and obj.vy <= 0:
            # On vient d'atteindre le pic
            self.ascending = False
            peak_height = obj.y
            self.just_bounced = False
            return peak_height
        elif self.ascending:
            # On continue de monter, mettre à jour la hauteur max
            self.max_height_after_bounce = max(self.max_height_after_bounce, obj.y)

        return 0.0

    def check_stop_condition(self, obj: PhysicsObject) -> bool:
        """
        Vérifie si la balle doit s'arrêter (vitesse et hauteur très faibles)
        """
        if (obj.speed < self.stop_threshold_speed and
                obj.y - obj.radius <= self.ground_level + self.stop_threshold_height):
            obj.vx = 0
            obj.vy = 0
            obj.y = self.ground_level + obj.radius
            self.simulation_stopped = True
            return True
        return False

    def update_object(self, obj: PhysicsObject, dt: float, numerical_method) -> Tuple[bool, float]:
        """
        Met à jour la position et vitesse de l'objet

        Returns:
            (collision_detected, peak_height_if_reached)
        """
        if self.simulation_stopped:
            return False, 0.0

        # Sauvegarder la position précédente
        self.previous_y = obj.y

        # Fonction pour calculer les dérivées
        def derivatives(x, y, vx, vy):
            return self.calculate_derivatives(x, y, vx, vy, obj)

        # État actuel
        state = (obj.x, obj.y, obj.vx, obj.vy)

        # Calcul du nouvel état
        new_state = numerical_method.step(state, derivatives, dt)
        obj.x, obj.y, obj.vx, obj.vy = new_state

        # Vérification des conditions d'arrêt
        if self.check_stop_condition(obj):
            return False, 0.0

        # Suivi de la hauteur maximale
        peak_height = self.track_max_height(obj)

        # Vérification collision avec le sol
        collision = self.handle_ground_collision(obj)

        return collision, peak_height

    def reset(self):
        """Remet le moteur physique à zéro"""
        self.total_rebounds = 0
        self.simulation_stopped = False
        self.just_bounced = False
        self.max_height_after_bounce = 0.0
        self.previous_y = 0.0
        self.ascending = False

    def get_physics_info(self) -> dict:
        """Retourne les informations physiques"""
        return {
            'total_rebounds': self.total_rebounds,
            'simulation_stopped': self.simulation_stopped,
            'air_density_factor': self.air_density_factor,
            'stop_threshold_speed': self.stop_threshold_speed
        }