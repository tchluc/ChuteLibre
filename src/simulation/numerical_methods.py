"""Méthodes numériques pour la résolution d'équations différentielles"""

from abc import ABC, abstractmethod
from typing import Callable, Tuple

class NumericalMethod(ABC):
    """Classe abstraite pour les méthodes numériques"""

    @abstractmethod
    def step(self, state: Tuple[float, ...], derivatives: Callable, dt: float) -> Tuple[float, ...]:
        """Effectue un pas de calcul"""
        pass

class EulerMethod(NumericalMethod):
    """Méthode d'Euler pour la résolution numérique"""

    def step(self, state: Tuple[float, ...], derivatives: Callable, dt: float) -> Tuple[float, ...]:
        """
        Méthode d'Euler : y(t+dt) = y(t) + f(t,y) * dt

        Args:
            state: État actuel (x, y, vx, vy)
            derivatives: Fonction calculant les dérivées
            dt: Pas de temps

        Returns:
            Nouvel état après un pas de temps
        """
        x, y, vx, vy = state
        dx_dt, dy_dt, dvx_dt, dvy_dt = derivatives(x, y, vx, vy)

        new_x = x + dx_dt * dt
        new_y = y + dy_dt * dt
        new_vx = vx + dvx_dt * dt
        new_vy = vy + dvy_dt * dt

        return new_x, new_y, new_vx, new_vy