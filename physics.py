from config import g, dt

class PhysicsEngine:
    def __init__(self, m, k, e, wind_speed, h0):
        self.m = m
        self.k = k
        self.e = e
        self.wind_speed = wind_speed
        self.h0 = h0
        self.reset()

    def reset(self):
        """Réinitialise la simulation"""
        self.x = 0.0  # Position horizontale (m)
        self.y = self.h0  # Position verticale (m)
        self.vx = 0.0  # Vitesse horizontale (m/s)
        self.vy = 0.0  # Vitesse verticale (m/s)
        self.x_analytic = 0.0
        self.y_analytic = self.h0
        self.vx_analytic = 0.0
        self.vy_analytic = 0.0
        self.rebounds = 0
        self.t = 0.0
        self.times = []
        self.kinetic_energies = []
        self.potential_energies = []
        self.total_energies = []

    def update(self, paused=False):
        """Met à jour l'état de la simulation"""
        if paused:
            return

        # Solution numérique (Euler)
        F_gravity = -self.m * g
        F_friction_y = -self.k * self.vy
        F_wind = self.k * self.wind_speed  # Force horizontale due au vent
        ax = F_wind / self.m
        ay = (F_gravity + F_friction_y) / self.m
        self.vx += ax * dt
        self.vy += ay * dt
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Solution analytique (sans frottement)
        ay_analytic = -g
        self.vy_analytic += ay_analytic * dt
        self.y_analytic += self.vy_analytic * dt
        self.x_analytic += self.vx_analytic * dt

        # Vérification du rebond (numérique)
        if self.y <= 0 and self.vy < 0:
            self.vy = -self.e * self.vy
            self.vx *= self.e  # Réduction de la vitesse horizontale
            self.y = 0
            self.rebounds += 1

        # Vérification du rebond (analytique)
        if self.y_analytic <= 0 and self.vy_analytic < 0:
            self.vy_analytic = -self.e * self.vy_analytic
            self.y_analytic = 0

        # Calcul des énergies
        kinetic_energy = 0.5 * self.m * (self.vx**2 + self.vy**2)
        potential_energy = self.m * g * self.y
        total_energy = kinetic_energy + potential_energy

        # Stockage pour le graphique
        self.times.append(self.t)
        self.kinetic_energies.append(kinetic_energy)
        self.potential_energies.append(potential_energy)
        self.total_energies.append(total_energy)

        # Limiter la taille des listes
        if len(self.times) > 200:
            self.times.pop(0)
            self.kinetic_energies.pop(0)
            self.potential_energies.pop(0)
            self.total_energies.pop(0)

        self.t += dt

    def update_parameters(self, m=None, k=None, e=None, wind_speed=None, h0=None):
        """Met à jour les paramètres de la simulation"""
        reset_needed = False

        if m is not None:
            self.m = m
        if k is not None:
            self.k = k
        if e is not None:
            self.e = e
        if wind_speed is not None:
            self.wind_speed = wind_speed
        if h0 is not None and h0 != self.h0:
            self.h0 = h0
            reset_needed = True

        if reset_needed:
            self.reset()