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

    def animate(self):
        # Configuration de l'interface avec 4 graphiques (2x2)
        fig = plt.figure(figsize=(12, 12))

        # 1. Animation de la chute
        ax1 = fig.add_subplot(2, 2, 1)
        ax1.set_xlim(-1, 1)
        ax1.set_ylim(-1, self.y0 + 1)
        ax1.set_xlabel("Position horizontale (m)")
        ax1.set_ylabel("Hauteur (m)")
        ax1.set_title("Chute libre avec rebond")
        ax1.grid(True)
        ground, = ax1.plot([-1, 1], [0, 0], 'k-', lw=2)
        ball = plt.Circle((0, self.y[0]), 0.2, color='blue')
        ax1.add_patch(ball)
        time_text = ax1.text(0.05, 0.95, '', transform=ax1.transAxes)

        # 2. Graphe temporel des énergies (dynamique)
        ax2 = fig.add_subplot(2, 2, 2)
        ax2.set_xlim(0, self.T)
        ax2.set_ylim(0, max(self.E_total) * 1.1)
        ax2.set_xlabel("Temps (s)")
        ax2.set_ylabel("Énergie (J)")
        ax2.set_title("Énergies en fonction du temps")
        ax2.grid(True)
        line_Ec, = ax2.plot([], [], label="Énergie cinétique (J)")
        line_Ep, = ax2.plot([], [], label="Énergie potentielle (J)")
        line_Etotal, = ax2.plot([], [], label="Énergie totale (J)", linestyle='--')
        ax2.legend()

        # 3. Graphe temporel de la hauteur (dynamique)
        ax3 = fig.add_subplot(2, 2, 3)
        ax3.set_xlim(0, self.T)
        ax3.set_ylim(-1, self.y0 + 1)
        ax3.set_xlabel("Temps (s)")
        ax3.set_ylabel("Hauteur (m)")
        ax3.set_title("Hauteur en fonction du temps")
        ax3.grid(True)
        line_y, = ax3.plot([], [], color='green')

        # 4. Graphe des hauteurs maximales par rebond (dynamique)
        ax4 = fig.add_subplot(2, 2, 4)
        ax4.set_xlim(-1, len(self.max_heights))  # Limite pour le nombre de rebonds
        ax4.set_ylim(-1, self.y0 + 1)
        ax4.set_xlabel("Numéro du rebond")
        ax4.set_ylabel("Hauteur maximale (m)")
        ax4.set_title("Hauteur maximale par rebond")
        ax4.grid(True)
        line_max_height, = ax4.plot([], [], marker='o', color='red')

        # Fonction d'initialisation pour l'animation
        def init():
            ball.center = (0, self.y[0])
            time_text.set_text('')
            line_Ec.set_data([], [])
            line_Ep.set_data([], [])
            line_Etotal.set_data([], [])
            line_y.set_data([], [])
            line_max_height.set_data([], [])
            return ball, time_text, line_Ec, line_Ep, line_Etotal, line_y, line_max_height

        # Fonction de mise à jour pour chaque frame
        def update(frame):
            # Mise à jour de la position de la balle
            ball.center = (0, self.y[frame])
            # Mise à jour du texte du temps
            time_text.set_text(f'Temps: {self.t[frame]:.2f} s')
            # Mise à jour des graphes d'énergie
            line_Ec.set_data(self.t[:frame+1], self.Ec[:frame+1])
            line_Ep.set_data(self.t[:frame+1], self.Ep[:frame+1])
            line_Etotal.set_data(self.t[:frame+1], self.E_total[:frame+1])
            # Mise à jour du graphe de la hauteur
            line_y.set_data(self.t[:frame+1], self.y[:frame+1])
            # Mise à jour du graphe des hauteurs maximales
            # Compter combien de maximums ont été atteints jusqu'à t[frame]
            current_max_heights = []
            current_rebound_numbers = []
            for i in range(len(self.max_times)):
                if self.max_times[i] <= self.t[frame]:
                    current_max_heights.append(self.max_heights[i])
                    current_rebound_numbers.append(i)
            line_max_height.set_data(current_rebound_numbers, current_max_heights)
            return ball, time_text, line_Ec, line_Ep, line_Etotal, line_y, line_max_height

        # Créer l'animation
        ani = animation.FuncAnimation(fig, update, frames=self.n_steps, init_func=init, blit=True, interval=self.dt*1000)

        plt.tight_layout()
        plt.show()

# Exemple d'utilisation
if __name__ == "__main__":
    # Paramètres
    m = 1.0
    y0 = 10.0
    v0 = 0.0
    dt = 0.01
    T = 10.0
    k = 0.1
    e = 0.8

    # Créer une instance de ChuteLibre et lancer la simulation
    chute = ChuteLibre(m, y0, v0, dt, T, k, e)
    chute.simulate()
    chute.animate()