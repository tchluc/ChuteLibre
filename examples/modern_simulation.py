"""Simulation d'une seule balle avec frottement et comptage de rebonds"""


import pygame.gfxdraw
import sys
import os

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.simulation.simulator import FreeFallSimulator
from src.models.physics_object import PhysicsObject
from src.simulation.numerical_methods import EulerMethod
from src.visualization.modern_ui import *
from src.utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT, SCALE, INITIAL_HEIGHTS, BALL_TYPES, GROUND_TYPES, AIR_DENSITY_FACTORS, BALL_RADIUS, FPS


class SingleBallSimulationApp:
    """Application de simulation d'une seule balle"""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Simulation Balle Rebondissante - Dissipation d'Énergie")
        self.clock = pygame.time.Clock()

        # État de l'application
        self.state = "config"  # "config" ou "simulation"
        self.running = True
        self.paused = False

        # Sélections utilisateur
        self.selected_ball = 0
        self.selected_ground = 0
        self.selected_air_density = 2  # Air normal par défaut
        self.selected_height = 3  # 10m par défaut

        # Simulateur
        self.simulator = None
        self.init_simulator()

        # Données pour graphiques (plus de points pour voir la dissipation complète)
        self.energy_data = {
            'time': [],
            'kinetic': [],
            'potential': [],
            'total': [],
            'rebounds': []  # Marquer les moments de rebond
        }

        # Statistiques de rebonds
        self.bounce_heights = []  # Hauteurs successives après chaque rebond
        self.bounce_times = []    # Temps de chaque rebond

    def init_simulator(self):
        """Initialise le simulateur"""
        ball_config = BALL_TYPES[self.selected_ball]
        ground_config = GROUND_TYPES[self.selected_ground]
        air_config = AIR_DENSITY_FACTORS[self.selected_air_density]

        self.simulator = FreeFallSimulator(
            dt=0.002,  # Pas de temps plus petit pour plus de précision
            air_resistance=True,
            ground_level=0.0,
            air_density_factor=air_config["factor"],
            numerical_method=EulerMethod()
        )

        # Objet physique
        initial_height = INITIAL_HEIGHTS[self.selected_height]

        obj = PhysicsObject(
            x=0, y=initial_height, vx=0, vy=0,
            mass=ball_config["mass"],
            radius=ball_config["radius"],
            drag_coefficient=ball_config["drag_coefficient"],
            restitution_coefficient=ground_config["restitution"],
            color=ball_config["color"]
        )

        self.simulator.add_object(obj)

    def reset_simulation(self):
        """Remet la simulation à zéro"""
        self.simulator.reset()
        self.simulator.physics_engine.reset()
        self.energy_data = {'time': [], 'kinetic': [], 'potential': [], 'total': [], 'rebounds': []}
        self.bounce_heights = []
        self.bounce_times = []
        self.init_simulator()
        self.simulator.start()

    def update_simulation(self):
        """Met à jour la simulation"""
        if not self.paused and self.state == "simulation" and not self.simulator.physics_engine.simulation_stopped:
            previous_rebounds = self.simulator.physics_engine.total_rebounds

            # Mettre à jour la simulation et récupérer la hauteur de pic si atteinte
            collision, peak_height = self.simulator.physics_engine.update_object(
                self.simulator.objects[0],
                self.simulator.dt,
                self.simulator.numerical_method
            )

            # Mise à jour du temps de simulation
            self.simulator.time += self.simulator.dt

            # Vérifier s'il y a eu un nouveau rebond (collision avec le sol)
            current_rebounds = self.simulator.physics_engine.total_rebounds
            if current_rebounds > previous_rebounds:
                # Un nouveau rebond s'est produit, on attend la hauteur max
                obj = self.simulator.objects[0]
                self.bounce_times.append(self.simulator.time)

            # Vérifier si on a atteint une hauteur maximale après un rebond
            if peak_height > 0:
                self.bounce_heights.append(peak_height)
                print(f"Rebond {len(self.bounce_heights)}: hauteur max = {peak_height:.3f}m")

            # Mise à jour de l'historique de l'objet
            if self.simulator.objects:
                obj = self.simulator.objects[0]
                obj.update_history(self.simulator.time, self.simulator.physics_engine.ground_level)

            # Mise à jour des données d'énergie
            if self.simulator.objects:
                obj = self.simulator.objects[0]
                ke = obj.kinetic_energy
                pe = obj.potential_energy(0)
                total = ke + pe

                self.energy_data['time'].append(self.simulator.time)
                self.energy_data['kinetic'].append(ke)
                self.energy_data['potential'].append(pe)
                self.energy_data['total'].append(total)

                # Marquer les rebonds (quand on atteint la hauteur max)
                if peak_height > 0:
                    self.energy_data['rebounds'].append(len(self.energy_data['time']) - 1)

                # Limiter la taille des données
                max_points = 1000
                if len(self.energy_data['time']) > max_points:
                    # Garder les derniers points
                    for key in ['time', 'kinetic', 'potential', 'total']:
                        self.energy_data[key] = self.energy_data[key][-max_points:]

                    # Ajuster les indices de rebonds
                    self.energy_data['rebounds'] = [idx - (len(self.energy_data['time']) - max_points)
                                                    for idx in self.energy_data['rebounds']
                                                    if idx >= len(self.energy_data['time']) - max_points]



    def draw_header(self, title: str):
        """Dessine l'en-tête moderne"""
        header_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 80)
        pygame.draw.rect(self.screen, ModernColors.PRIMARY, header_rect)

        title_font = pygame.font.SysFont("Arial", 28, bold=True)
        title_surface = title_font.render(title, True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 40))
        self.screen.blit(title_surface, title_rect)

    def draw_bounce_table(self, x: int, y: int, width: int, height: int):
        """Dessine le tableau des hauteurs de rebonds"""
        table_card = ModernCard(x, y, width, height, "Hauteurs des Rebonds")
        table_card.draw(self.screen)

        if not self.bounce_heights:
            no_data_text = pygame.font.SysFont("Arial", 14).render("Aucun rebond pour le moment", True, ModernColors.TEXT_LIGHT)
            text_rect = no_data_text.get_rect(center=(x + width // 2, y + height // 2))
            self.screen.blit(no_data_text, text_rect)
            return

        # En-têtes du tableau
        header_font = pygame.font.SysFont("Arial", 12, bold=True)
        data_font = pygame.font.SysFont("Arial", 11)

        header_y = y + 50
        row_height = 20

        # En-têtes
        headers = ["#", "Hauteur (m)", "Temps (s)", "Perte (%)"]
        col_widths = [30, 80, 70, 70]
        col_x = x + 20

        for i, (header, col_width) in enumerate(zip(headers, col_widths)):
            header_rect = pygame.Rect(col_x, header_y, col_width, row_height)
            pygame.draw.rect(self.screen, ModernColors.BORDER, header_rect, 1)

            header_surface = header_font.render(header, True, ModernColors.PRIMARY)
            header_text_rect = header_surface.get_rect(center=header_rect.center)
            self.screen.blit(header_surface, header_text_rect)

            col_x += col_width

        # Données
        initial_height = INITIAL_HEIGHTS[self.selected_height]
        visible_rows = min(len(self.bounce_heights), (height - 90) // row_height)
        start_idx = max(0, len(self.bounce_heights) - visible_rows)

        for i in range(visible_rows):
            data_idx = start_idx + i
            if data_idx >= len(self.bounce_heights):
                break

            bounce_num = data_idx + 1
            bounce_height = self.bounce_heights[data_idx]
            bounce_time = self.bounce_times[data_idx]

            # Calcul de la perte (par rapport à la hauteur précédente)
            if data_idx == 0:
                previous_height = initial_height
            else:
                previous_height = self.bounce_heights[data_idx - 1]

            height_loss = ((previous_height - bounce_height) / previous_height) * 100 if previous_height > 0 else 0

            row_y = header_y + (i + 1) * row_height
            col_x = x + 20

            # Alternance de couleur des lignes
            if i % 2 == 1:
                row_rect = pygame.Rect(col_x, row_y, sum(col_widths), row_height)
                pygame.draw.rect(self.screen, (245, 245, 245), row_rect)

            # Données de la ligne
            row_data = [
                str(bounce_num),
                f"{bounce_height:.3f}",
                f"{bounce_time:.2f}",
                f"{height_loss:.1f}"
            ]

            for j, (data, col_width) in enumerate(zip(row_data, col_widths)):
                data_rect = pygame.Rect(col_x, row_y, col_width, row_height)
                pygame.draw.rect(self.screen, ModernColors.BORDER, data_rect, 1)

                # Couleur spéciale pour les pertes élevées
                text_color = ModernColors.DANGER if j == 3 and float(data.replace('%', '')) > 50 else ModernColors.TEXT

                data_surface = data_font.render(data, True, text_color)
                data_text_rect = data_surface.get_rect(center=data_rect.center)
                self.screen.blit(data_surface, data_text_rect)

                col_x += col_width

        # Indicateur s'il y a plus de rebonds
        if len(self.bounce_heights) > visible_rows:
            more_text = f"... et {len(self.bounce_heights) - visible_rows} rebonds précédents"
            more_surface = pygame.font.SysFont("Arial", 10).render(more_text, True, ModernColors.TEXT_LIGHT)
            self.screen.blit(more_surface, (x + 20, y + height - 25))

        # Statistiques rapides du tableau
        if len(self.bounce_heights) >= 2:
            avg_loss = sum((self.bounce_heights[i-1] - self.bounce_heights[i]) / self.bounce_heights[i-1] * 100
                           for i in range(1, len(self.bounce_heights))) / (len(self.bounce_heights) - 1)

            stats_y = y + height - 45
            stats_text = f"Perte moyenne par rebond: {avg_loss:.1f}%"
            stats_surface = pygame.font.SysFont("Arial", 11, bold=True).render(stats_text, True, ModernColors.PRIMARY)
            self.screen.blit(stats_surface, (x + 20, stats_y))

    def draw_energy_graph(self, x: int, y: int, width: int, height: int):
        """Dessine le graphique d'énergie avec dissipation"""
        graph_card = ModernCard(x, y, width, height, "Dissipation d'Énergie au Fil du Temps")
        graph_card.draw(self.screen)

        if len(self.energy_data['time']) < 2:
            return

        # Zone de dessin
        plot_x = x + 80
        plot_y = y + 50
        plot_width = width - 100
        plot_height = height - 90

        # Valeurs min/max pour normalisation
        max_energy = max(max(self.energy_data['total'], default=[1]), 1)
        max_time = max(self.energy_data['time']) if self.energy_data['time'] else 1

        # Grille horizontale (énergie)
        for i in range(1, 6):
            grid_y = plot_y + plot_height - i * plot_height // 5
            pygame.draw.line(self.screen, ModernColors.GRID,
                             (plot_x, grid_y), (plot_x + plot_width, grid_y), 1)

            energy_val = i * max_energy / 5
            label = pygame.font.SysFont("Arial", 10).render(f"{energy_val:.2f}J", True, ModernColors.TEXT_LIGHT)
            self.screen.blit(label, (x + 10, grid_y - 5))

        # Grille verticale (temps)
        for i in range(1, 6):
            grid_x = plot_x + i * plot_width // 5
            pygame.draw.line(self.screen, ModernColors.GRID,
                             (grid_x, plot_y), (grid_x, plot_y + plot_height), 1)

            time_val = i * max_time / 5
            label = pygame.font.SysFont("Arial", 10).render(f"{time_val:.1f}s", True, ModernColors.TEXT_LIGHT)
            self.screen.blit(label, (grid_x - 10, plot_y + plot_height + 5))

        # Axes
        pygame.draw.line(self.screen, ModernColors.TEXT,
                         (plot_x, plot_y), (plot_x, plot_y + plot_height), 2)
        pygame.draw.line(self.screen, ModernColors.TEXT,
                         (plot_x, plot_y + plot_height), (plot_x + plot_width, plot_y + plot_height), 2)

        # Labels des axes
        energy_label = pygame.font.SysFont("Arial", 10, bold=True).render("Énergie (J)", True, ModernColors.TEXT)
        # Rotation du texte pour l'axe Y
        energy_label_rotated = pygame.transform.rotate(energy_label, 90)
        self.screen.blit(energy_label_rotated, (x + 5, plot_y + plot_height // 2 - 30))

        time_label = pygame.font.SysFont("Arial", 10, bold=True).render("Temps (s)", True, ModernColors.TEXT)
        self.screen.blit(time_label, (plot_x + plot_width // 2 - 30, plot_y + plot_height + 25))

        # Légende
        legend_items = [
            (ModernColors.DANGER, "Cinétique"),
            (ModernColors.SECONDARY, "Potentielle"),
            (ModernColors.BALL2, "Totale"),
            (ModernColors.WARNING, "Rebonds")
        ]

        for i, (color, label) in enumerate(legend_items):
            legend_x = plot_x + i * 120
            legend_y = y + 20
            pygame.draw.rect(self.screen, color, (legend_x, legend_y, 12, 12))
            text = pygame.font.SysFont("Arial", 12).render(label, True, ModernColors.TEXT)
            self.screen.blit(text, (legend_x + 15, legend_y))

        # Courbes d'énergie
        if len(self.energy_data['time']) > 1:
            curves = [
                (self.energy_data['kinetic'], ModernColors.DANGER, 2),
                (self.energy_data['potential'], ModernColors.SECONDARY, 2),
                (self.energy_data['total'], ModernColors.BALL2, 3)
            ]

            for data, color, thickness in curves:
                points = []
                for i, (time_val, energy_val) in enumerate(zip(self.energy_data['time'], data)):
                    px = plot_x + int(time_val / max_time * plot_width)
                    py = plot_y + plot_height - int(energy_val / max_energy * plot_height)
                    points.append((px, py))

                if len(points) > 1:
                    pygame.draw.lines(self.screen, color, False, points, thickness)

            # Marquer les rebonds
            for rebound_idx in self.energy_data['rebounds']:
                if rebound_idx < len(self.energy_data['time']):
                    time_val = self.energy_data['time'][rebound_idx]
                    energy_val = self.energy_data['total'][rebound_idx]

                    px = plot_x + int(time_val / max_time * plot_width)
                    py = plot_y + plot_height - int(energy_val / max_energy * plot_height)

                    # Ligne verticale pour marquer le rebond
                    pygame.draw.line(self.screen, ModernColors.WARNING,
                                     (px, plot_y), (px, plot_y + plot_height), 2)

                    # Cercle sur la courbe d'énergie totale
                    pygame.draw.circle(self.screen, ModernColors.WARNING, (px, py), 4)

        # Affichage de la perte d'énergie
        if len(self.energy_data['total']) > 1:
            initial_energy = self.energy_data['total'][0]
            current_energy = self.energy_data['total'][-1]
            energy_loss = initial_energy - current_energy
            loss_percentage = (energy_loss / initial_energy) * 100 if initial_energy > 0 else 0

            loss_text = f"Perte d'énergie: {energy_loss:.3f}J ({loss_percentage:.1f}%)"
            loss_surface = pygame.font.SysFont("Arial", 14, bold=True).render(loss_text, True, ModernColors.DANGER)
            self.screen.blit(loss_surface, (plot_x + plot_width - 250, plot_y + 10))

    def draw_simulation_area(self, x: int, y: int, width: int, height: int):
        """Dessine la zone de simulation"""
        sim_card = ModernCard(x, y, width, height, "Zone de Simulation")
        sim_card.draw(self.screen)

        # Zone de dessin
        sim_x = x + 20
        sim_y = y + 50
        sim_width = width - 40
        sim_height = height - 90

        # Sol avec effet
        ground_y = sim_y + sim_height - 40
        pygame.draw.line(self.screen, ModernColors.TEXT,
                         (sim_x, ground_y), (sim_x + sim_width, ground_y), 4)

        # Effet d'ombre du sol
        for i in range(1, 4):
            alpha = 100 - i * 25
            pygame.draw.line(self.screen, (*ModernColors.TEXT, alpha),
                             (sim_x, ground_y + i), (sim_x + sim_width, ground_y + i), 1)

        # Grille de référence
        origin_x = sim_x + 80
        max_height = INITIAL_HEIGHTS[self.selected_height]

        # Lignes horizontales (hauteur)
        for i in range(0, int(max_height) + 1):
            grid_y = ground_y - i * SCALE
            if grid_y > sim_y:
                pygame.draw.line(self.screen, ModernColors.GRID,
                                 (sim_x, grid_y), (sim_x + sim_width, grid_y), 1)

                height_text = pygame.font.SysFont("Arial", 11).render(f"{i}m", True, ModernColors.TEXT_LIGHT)
                self.screen.blit(height_text, (sim_x + 5, grid_y - 6))

        # Lignes verticales (temps simulé)
        for i in range(0, int(sim_width // 80) + 1):
            grid_x = origin_x + i * 80
            if grid_x < sim_x + sim_width:
                pygame.draw.line(self.screen, ModernColors.GRID,
                                 (grid_x, sim_y), (grid_x, ground_y), 1)

        # Objet en simulation
        if self.simulator.objects:
            obj = self.simulator.objects[0]

            # Position à l'écran
            ball_x = origin_x + int(obj.x * SCALE * 0.5)  # Facteur pour centrer
            ball_y = ground_y - int(obj.y * SCALE)

            # Trajectoire (trace des dernières positions)
            if len(obj.history['x']) > 1:
                trail_points = []
                trail_length = min(50, len(obj.history['x']))
                for i in range(len(obj.history['x']) - trail_length, len(obj.history['x'])):
                    trail_x = origin_x + int(obj.history['x'][i] * SCALE * 0.5)
                    trail_y = ground_y - int(obj.history['y'][i] * SCALE)
                    trail_points.append((trail_x, trail_y))

                # Dessiner la trace avec transparence décroissante
                for i in range(1, len(trail_points)):
                    alpha = int(255 * (i / len(trail_points)) * 0.3)
                    color = (*ModernColors.TEXT_LIGHT, alpha)
                    if i < len(trail_points) - 1:
                        pygame.draw.line(self.screen, ModernColors.TEXT_LIGHT,
                                         trail_points[i], trail_points[i+1], 1)

            # Ombre de la balle
            shadow_radius = max(3, BALL_RADIUS - int(obj.y * 1.5))
            shadow_alpha = max(30, 120 - int(obj.y * 10))
            pygame.draw.ellipse(self.screen, (0, 0, 0, shadow_alpha),
                                (ball_x - shadow_radius, ground_y - 3, shadow_radius * 2, 8))

            # Balle principale
            pygame.gfxdraw.filled_circle(self.screen, ball_x, ball_y, BALL_RADIUS, ModernColors.BALL1)
            pygame.gfxdraw.aacircle(self.screen, ball_x, ball_y, BALL_RADIUS, ModernColors.BALL1)

            # Effet de brillance
            pygame.gfxdraw.filled_circle(self.screen, ball_x - 4, ball_y - 4, 4, (255, 255, 255, 180))

            # Vecteur vitesse si en mouvement
            if obj.speed > 0.1:
                vel_scale = 30
                end_x = ball_x + int(obj.vx * vel_scale)
                end_y = ball_y - int(obj.vy * vel_scale)

                # Limiter la longueur du vecteur
                max_length = 50
                dx, dy = end_x - ball_x, end_y - ball_y
                length = math.sqrt(dx*dx + dy*dy)
                if length > max_length:
                    end_x = ball_x + int(dx * max_length / length)
                    end_y = ball_y + int(dy * max_length / length)

                pygame.draw.line(self.screen, ModernColors.WARNING, (ball_x, ball_y), (end_x, end_y), 3)
                pygame.draw.circle(self.screen, ModernColors.WARNING, (end_x, end_y), 4)

        # Indicateur d'état de simulation
        status_y = sim_y + sim_height - 20
        if self.simulator.physics_engine.simulation_stopped:
            status_text = "🛑 SIMULATION TERMINÉE - Balle arrêtée"
            status_color = ModernColors.DANGER
        elif self.paused:
            status_text = "⏸️ SIMULATION EN PAUSE"
            status_color = ModernColors.WARNING
        else:
            status_text = "▶️ SIMULATION EN COURS"
            status_color = ModernColors.SECONDARY

        status_surface = pygame.font.SysFont("Arial", 14, bold=True).render(status_text, True, status_color)
        self.screen.blit(status_surface, (sim_x + 10, status_y))

    def draw_stats_panel(self, x: int, y: int, width: int, height: int):
        """Dessine le panneau de statistiques détaillées"""
        stats_card = ModernCard(x, y, width, height, "Statistiques Détaillées")
        stats_card.draw(self.screen)

        if not self.simulator.objects:
            return

        obj = self.simulator.objects[0]
        physics_info = self.simulator.physics_engine.get_physics_info()
        font = pygame.font.SysFont("Arial", 13)
        title_font = pygame.font.SysFont("Arial", 14, bold=True)
        y_offset = 50

        # Section Objet
        section_title = title_font.render("OBJET", True, ModernColors.PRIMARY)
        self.screen.blit(section_title, (x + 20, y + y_offset))
        y_offset += 25

        object_stats = [
            ("Type", BALL_TYPES[self.selected_ball]["name"]),
            ("Masse", f"{obj.mass:.3f} kg"),
            ("Rayon", f"{obj.radius:.3f} m"),
            ("Coeff. traînée", f"{obj.drag_coefficient:.3f}")
        ]

        for label, value in object_stats:
            self._draw_stat_line(x, y + y_offset, width, label, value, font)
            y_offset += 20

        y_offset += 10

        # Section Environnement
        section_title = title_font.render("ENVIRONNEMENT", True, ModernColors.PRIMARY)
        self.screen.blit(section_title, (x + 20, y + y_offset))
        y_offset += 25

        env_stats = [
            ("Sol", GROUND_TYPES[self.selected_ground]["name"]),
            ("Coeff. restitution", f"{obj.restitution_coefficient:.2f}"),
            ("Densité air", f"{physics_info['air_density_factor']:.1f}x"),
            ("Hauteur initiale", f"{INITIAL_HEIGHTS[self.selected_height]:.1f} m")
        ]

        for label, value in env_stats:
            self._draw_stat_line(x, y + y_offset, width, label, value, font)
            y_offset += 20

        y_offset += 10

        # Section État Actuel
        section_title = title_font.render("ÉTAT ACTUEL", True, ModernColors.PRIMARY)
        self.screen.blit(section_title, (x + 20, y + y_offset))
        y_offset += 25

        current_stats = [
            ("Temps", f"{self.simulator.time:.2f} s"),
            ("Position Y", f"{obj.y:.3f} m"),
            ("Vitesse", f"{obj.speed:.3f} m/s"),
            ("Vitesse X", f"{obj.vx:.3f} m/s"),
            ("Vitesse Y", f"{obj.vy:.3f} m/s")
        ]

        for label, value in current_stats:
            self._draw_stat_line(x, y + y_offset, width, label, value, font)
            y_offset += 20

        y_offset += 10

        # Section Énergies
        section_title = title_font.render("ÉNERGIES", True, ModernColors.PRIMARY)
        self.screen.blit(section_title, (x + 20, y + y_offset))
        y_offset += 25

        ke = obj.kinetic_energy
        pe = obj.potential_energy(0)
        total_energy = ke + pe

        if len(self.energy_data['total']) > 0:
            initial_energy = self.energy_data['total'][0]
            energy_loss = initial_energy - total_energy
            loss_percentage = (energy_loss / initial_energy) * 100 if initial_energy > 0 else 0
        else:
            energy_loss = 0
            loss_percentage = 0

        energy_stats = [
            ("Cinétique", f"{ke:.4f} J"),
            ("Potentielle", f"{pe:.4f} J"),
            ("Totale", f"{total_energy:.4f} J"),
            ("Perte totale", f"{energy_loss:.4f} J"),
            ("Perte (%)", f"{loss_percentage:.2f} %")
        ]

        for i, (label, value) in enumerate(energy_stats):
            color = ModernColors.DANGER if i >= 3 else ModernColors.TEXT
            self._draw_stat_line(x, y + y_offset, width, label, value, font, value_color=color)
            y_offset += 20

        y_offset += 10

        # Section Rebonds
        section_title = title_font.render("REBONDS", True, ModernColors.PRIMARY)
        self.screen.blit(section_title, (x + 20, y + y_offset))
        y_offset += 25

        # Calcul de la hauteur max du dernier rebond
        last_bounce_height = max(self.bounce_heights) if self.bounce_heights else 0

        bounce_stats = [
            ("Nombre total", f"{physics_info['total_rebounds']}"),
            ("Dernière hauteur", f"{last_bounce_height:.3f} m"),
            ("Seuil d'arrêt", f"{physics_info['stop_threshold_speed']:.3f} m/s"),
            ("État", "Arrêtée" if physics_info['simulation_stopped'] else "En cours")
        ]

        for label, value in bounce_stats:
            color = ModernColors.DANGER if label == "État" and physics_info['simulation_stopped'] else ModernColors.TEXT
            self._draw_stat_line(x, y + y_offset, width, label, value, font, value_color=color)
            y_offset += 20

    def _draw_stat_line(self, x: int, y: int, width: int, label: str, value: str, font: pygame.font.Font, value_color=None):
        """Dessine une ligne de statistique"""
        if value_color is None:
            value_color = ModernColors.TEXT

        label_text = font.render(f"{label}:", True, ModernColors.TEXT_LIGHT)
        value_text = font.render(str(value), True, value_color)

        self.screen.blit(label_text, (x + 30, y))
        self.screen.blit(value_text, (x + width - 30 - value_text.get_width(), y))

    def draw_config_screen(self):
        """Dessine l'écran de configuration"""
        self.screen.fill(ModernColors.BACKGROUND)
        self.draw_header(f"Configuration - Simulation Balle Rebondissante")

        # Interface de configuration
        main_card = ModernCard(50, 100, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 170)
        main_card.draw(self.screen)

        # Colonne gauche - Sélecteurs
        col1_x = 80
        col1_width = 500
        y_start = 150

        config_card = ModernCard(col1_x, y_start, col1_width, 350, "Paramètres de Simulation")
        config_card.draw(self.screen)

        ball_selector = ModernSelector(col1_x + 20, y_start + 60, col1_width - 40, BALL_TYPES, self.selected_ball, "Type de balle")
        ground_selector = ModernSelector(col1_x + 20, y_start + 120, col1_width - 40, GROUND_TYPES, self.selected_ground, "Type de sol")
        air_selector = ModernSelector(col1_x + 20, y_start + 180, col1_width - 40, AIR_DENSITY_FACTORS, self.selected_air_density, "Densité d'air")
        height_selector = ModernSelector(col1_x + 20, y_start + 240, col1_width - 40, [f"{h} m" for h in INITIAL_HEIGHTS], self.selected_height, "Hauteur initiale")

        ball_selector.draw(self.screen)
        ground_selector.draw(self.screen)
        air_selector.draw(self.screen)
        height_selector.draw(self.screen)

        # Colonne droite - Tableau des rebonds de la dernière simulation
        col2_x = col1_x + col1_width + 50
        col2_width = 600

        self.draw_bounce_table(col2_x, y_start, col2_width, 350)

        # Section d'explication
        explanation_card = ModernCard(col1_x, y_start + 380, col1_width + col2_width + 50, 180, "À propos de cette simulation")
        explanation_card.draw(self.screen)

        explanation_text = [
            "Cette simulation modélise une balle rebondissante avec :",
            "• Frottement de l'air proportionnel au carré de la vitesse",
            "• Perte d'énergie à chaque rebond selon le coefficient de restitution",
            "• Arrêt automatique quand l'énergie devient négligeable",
            "• Comptage précis du nombre de rebonds avec tableau des hauteurs",
            "• Visualisation de la dissipation d'énergie complète jusqu'à l'arrêt"
        ]

        exp_font = pygame.font.SysFont("Arial", 13)
        exp_y = y_start + 430

        for i, line in enumerate(explanation_text):
            color = ModernColors.PRIMARY if i == 0 else ModernColors.TEXT
            weight = True if i == 0 else False
            line_font = pygame.font.SysFont("Arial", 13, bold=weight)
            text_surface = line_font.render(line, True, color)
            self.screen.blit(text_surface, (col1_x + 20, exp_y + i * 20))

        # Bouton de démarrage
        start_button = ModernButton(SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT - 60, 240, 50, "Démarrer la Simulation", 'secondary', 18)
        start_button.update(pygame.mouse.get_pos(), self.clock.get_time() / 1000.0)
        start_button.draw(self.screen)

        return start_button, ball_selector, ground_selector, air_selector, height_selector

    def draw_simulation_screen(self):
        """Dessine l'écran de simulation"""
        self.screen.fill(ModernColors.BACKGROUND)
        self.draw_header("Simulation de Dissipation d'Énergie")

        # Boutons de contrôle
        dt = self.clock.get_time() / 1000.0
        mouse_pos = pygame.mouse.get_pos()

        pause_text = "Reprendre" if self.paused else "Pause"
        pause_button = ModernButton(SCREEN_WIDTH - 530, 15, 120, 50, pause_text, 'warning')
        reset_button = ModernButton(SCREEN_WIDTH - 400, 15, 120, 50, "Reset", 'danger')
        config_button = ModernButton(SCREEN_WIDTH - 270, 15, 120, 50, "Config", 'secondary')

        # Affichage du nombre de rebonds dans l'en-tête
        if self.simulator:
            rebounds_text = f"Rebonds: {self.simulator.physics_engine.total_rebounds}"
            rebounds_font = pygame.font.SysFont("Arial", 20, bold=True)
            rebounds_surface = rebounds_font.render(rebounds_text, True, (255, 255, 255))
            self.screen.blit(rebounds_surface, (50, 30))

        pause_button.update(mouse_pos, dt)
        reset_button.update(mouse_pos, dt)
        config_button.update(mouse_pos, dt)

        pause_button.draw(self.screen)
        reset_button.draw(self.screen)
        config_button.draw(self.screen)

        # Disposition optimisée
        col1_width = 420  # Zone de simulation
        col2_width = 500  # Graphique d'énergie
        col3_width = 280  # Tableau des rebonds
        col4_width = 180  # Statistiques

        # Zone de simulation (gauche)
        self.draw_simulation_area(20, 100, col1_width, 780)

        # Graphique d'énergie (centre-gauche)
        self.draw_energy_graph(col1_width + 40, 100, col2_width, 480)

        # Tableau des rebonds (centre-droite)
        self.draw_bounce_table(col1_width + col2_width + 60, 100, col3_width, 480)

        # Panneau de statistiques (droite)
        self.draw_stats_panel(col1_width + col2_width + col3_width + 80, 100, col4_width, 780)

        # Zone d'informations supplémentaires (bas centre)
        info_card = ModernCard(col1_width + 40, 600, col2_width + col3_width + 20, 280, "Informations sur les Rebonds")
        info_card.draw(self.screen)

        # Affichage des statistiques de rebonds
        if len(self.bounce_heights) > 0:
            info_y = 650
            info_font = pygame.font.SysFont("Arial", 13)
            title_font = pygame.font.SysFont("Arial", 14, bold=True)

            # Calculs statistiques
            initial_height = INITIAL_HEIGHTS[self.selected_height]
            total_bounces = len(self.bounce_heights)

            if total_bounces > 0:
                highest_bounce = max(self.bounce_heights)
                lowest_bounce = min(self.bounce_heights)
                avg_height = sum(self.bounce_heights) / total_bounces

                # Perte d'énergie totale
                if len(self.energy_data['total']) > 0:
                    initial_energy = self.energy_data['total'][0]
                    current_energy = self.energy_data['total'][-1]
                    total_energy_loss = ((initial_energy - current_energy) / initial_energy) * 100
                else:
                    total_energy_loss = 0

                # Temps total de simulation
                total_time = self.simulator.time

                info_stats = [
                    f"Nombre total de rebonds: {total_bounces}",
                    f"Rebond le plus haut: {highest_bounce:.3f} m",
                    f"Rebond le plus bas: {lowest_bounce:.3f} m",
                    f"Hauteur moyenne des rebonds: {avg_height:.3f} m",
                    f"Réduction de hauteur totale: {((initial_height - (highest_bounce if total_bounces > 0 else 0)) / initial_height) * 100:.1f}%",
                    f"Perte d'énergie totale: {total_energy_loss:.1f}%",
                    f"Temps total de simulation: {total_time:.2f} s",
                    f"Fréquence moyenne des rebonds: {total_bounces / total_time:.2f} rebonds/s" if total_time > 0 else "Fréquence: N/A"
                ]

                # Affichage en deux colonnes
                col_width = (col2_width + col3_width) // 2
                for i, stat in enumerate(info_stats):
                    col = i % 2
                    row = i // 2
                    x_pos = col1_width + 60 + col * col_width
                    y_pos = info_y + row * 25

                    stat_surface = info_font.render(stat, True, ModernColors.TEXT)
                    self.screen.blit(stat_surface, (x_pos, y_pos))
        else:
            no_bounce_text = "Aucun rebond détecté pour le moment"
            no_bounce_surface = pygame.font.SysFont("Arial", 16).render(no_bounce_text, True, ModernColors.TEXT_LIGHT)
            text_rect = no_bounce_surface.get_rect(center=(col1_width + 40 + (col2_width + col3_width) // 2, 740))
            self.screen.blit(no_bounce_surface, text_rect)

        return pause_button, reset_button, config_button

    async def run(self):
        """Boucle principale de l'application"""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0

            # Mise à jour de la simulation
            self.update_simulation()

            # Gestion des événements
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    await self.handle_click(event.pos)

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.paused = not self.paused
                    elif event.key == pygame.K_r:
                        self.reset_simulation()
                    elif event.key == pygame.K_ESCAPE:
                        if self.state == "simulation":
                            self.state = "config"

            # Rendu
            if self.state == "config":
                ui_elements = self.draw_config_screen()
                self.config_ui_elements = ui_elements
            else:
                ui_elements = self.draw_simulation_screen()
                self.sim_ui_elements = ui_elements

            pygame.display.flip()

            # Nécessaire pour la compatibilité web
            await asyncio.sleep(0)

    async def handle_click(self, pos):
        """Gère les clics de souris"""
        if self.state == "config":
            start_button, ball_selector, ground_selector, air_selector, height_selector = self.config_ui_elements

            if start_button.rect.collidepoint(pos):
                start_button.click()
                self.state = "simulation"
                self.reset_simulation()

            elif ball_selector.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=pos)):
                self.selected_ball = ball_selector.selected_index

            elif ground_selector.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=pos)):
                self.selected_ground = ground_selector.selected_index

            elif air_selector.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=pos)):
                self.selected_air_density = air_selector.selected_index

            elif height_selector.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=pos)):
                self.selected_height = height_selector.selected_index

        else:  # simulation
            pause_button, reset_button, config_button = self.sim_ui_elements

            if pause_button.rect.collidepoint(pos):
                pause_button.click()
                self.paused = not self.paused

            elif reset_button.rect.collidepoint(pos):
                reset_button.click()
                self.reset_simulation()

            elif config_button.rect.collidepoint(pos):
                config_button.click()
                self.state = "config"

async def main():
    """Point d'entrée principal"""
    app = SingleBallSimulationApp()
    await app.run()

if __name__ == "__main__":
    if platform.system() == "Emscripten":
        asyncio.ensure_future(main())
    else:
        asyncio.run(main())