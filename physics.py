import numpy as np

class ChuteLibre:
    g = 9.81  # Accélération due à la gravité (m/s^2)

    def __init__(self, m, y0, v0, dt, T, k, e):
        self.m = m
        self.y0 = y0
        self.v0 = v0
        self.dt = dt
        self.T = T
        self.k = k
        self.e = e

        self.n_steps = int(T / dt)
        self.t = np.linspace(0, T, self.n_steps)
        self.y = np.zeros(self.n_steps)
        self.v = np.zeros(self.n_steps)
        self.Ec = np.zeros(self.n_steps)  # Énergie cinétique
        self.Ep = np.zeros(self.n_steps)  # Énergie potentielle
        self.E_total = np.zeros(self.n_steps)  # Énergie totale

        # Initialisation des conditions initiales
        self.y[0] = self.y0
        self.v[0] = self.v0
        self.Ec[0] = self.kinetic_energy(self.v[0])
        self.Ep[0] = self.potential_energy(self.y[0])
        self.E_total[0] = self.Ec[0] + self.Ep[0]

        # Attributs pour la compatibilité avec l'interface UI
        self.selected_ball = 0
        self.selected_ground = 0
        self.current_step = 0
        self.time = 0

        # Exécute la simulation immédiatement
        self.simulate()

    def calcul_speed(self, current_speed):
        acceleration = -self.g - (self.k / self.m) * current_speed
        return current_speed + acceleration * self.dt

    def kinetic_energy(self, speed):
        return 0.5 * self.m * speed ** 2

    def potential_energy(self, height):
        return self.m * self.g * height

    def total_energy(self, kinetic, potential):
        return kinetic + potential

    def simulate(self):
        # Simulation avec méthode d'Euler explicite
        self.rebound_indices = []  # Pour stocker les indices des rebonds
        for i in range(1, self.n_steps):
            # Mise à jour de la vitesse
            self.v[i] = self.calcul_speed(self.v[i-1])
            # Mise à jour de la position
            self.y[i] = self.y[i-1] + self.v[i-1] * self.dt
            # Gestion du rebond
            if self.y[i] <= 0 and self.v[i] < 0:
                self.y[i] = 0
                self.v[i] = -self.e * self.v[i]
                self.rebound_indices.append(i)
            # Calcul des énergies
            self.Ec[i] = self.kinetic_energy(self.v[i])
            self.Ep[i] = self.potential_energy(self.y[i])
            self.E_total[i] = self.total_energy(self.Ec[i], self.Ep[i])

        # Calcul des hauteurs maximales après chaque rebond
        self.max_heights = [self.y0]  # Hauteur initiale comme premier maximum
        self.max_times = [0]  # Temps initial
        for i in self.rebound_indices:
            j = i
            while j < self.n_steps - 1 and self.y[j] < self.y[j + 1]:
                j += 1
            if j < self.n_steps:
                self.max_heights.append(self.y[j])
                self.max_times.append(self.t[j])

    def update(self, paused=False):
        """Met à jour la simulation si elle n'est pas en pause"""
        if not paused and self.current_step < self.n_steps - 1:
            self.current_step += 1
            self.time = self.t[self.current_step]

    def reset(self):
        """Réinitialise la simulation"""
        self.current_step = 0
        self.time = 0

    def update_parameters(self, **kwargs):
        """Met à jour les paramètres de simulation et réinitialise"""
        # Mettre à jour les paramètres avec les valeurs fournies
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

        # Réinitialiser les valeurs initiales si nécessaire
        if 'h0' in kwargs:
            self.y0 = kwargs['h0']

        # Réexécute la simulation avec les nouveaux paramètres
        self.__init__(self.m, self.y0, self.v0, self.dt, self.T, self.k, self.e)

    # Méthodes pour accéder aux données actuelles
    @property
    def position(self):
        """Retourne la position actuelle"""
        return self.y[self.current_step]

    @property
    def velocity(self):
        """Retourne la vitesse actuelle"""
        return self.v[self.current_step]

    # Méthodes pour accéder aux données historiques complètes
    def get_time_data(self):
        """Retourne toutes les données temporelles"""
        return self.t

    def get_position_data(self):
        """Retourne toutes les données de position"""
        return self.y

    def get_velocity_data(self):
        """Retourne toutes les données de vitesse"""
        return self.v

    def get_energy_data(self):
        """Retourne toutes les données d'énergie"""
        return self.Ec, self.Ep, self.E_total

    def get_max_heights(self):
        """Retourne les hauteurs maximales après chaque rebond"""
        return self.max_heights, self.max_times

    def get_rebound_indices(self):
        """Retourne les indices des rebonds"""
        return self.rebound_indices