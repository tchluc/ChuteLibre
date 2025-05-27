import asyncio
import platform
import pygame
import pygame.gfxdraw
import math

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

# Initialisation de Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Chute Libre - Configuration")
clock = pygame.time.Clock()

# Classes UI modernes
class ModernButton:
    def __init__(self, x, y, width, height, text, color_scheme='primary', font_size=16, icon=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color_scheme = color_scheme
        self.font = pygame.font.SysFont("Arial", font_size, bold=True)
        self.icon = icon
        self.is_hovered = False
        self.click_effect = 0

    def update(self, mouse_pos, dt):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        if self.click_effect > 0:
            self.click_effect = max(0, self.click_effect - dt * 5)

    def click(self):
        self.click_effect = 1.0

    def draw(self, screen):
        # Ombre
        shadow_rect = self.rect.copy()
        shadow_rect.x += 2
        shadow_rect.y += 2
        pygame.draw.rect(screen, COLORS['shadow'], shadow_rect, border_radius=8)

        # Bouton principal
        color = COLORS[f'{self.color_scheme}_hover'] if self.is_hovered else COLORS[self.color_scheme]
        if self.click_effect > 0:
            brightness = 1 - self.click_effect * 0.2
            color = tuple(int(c * brightness) for c in color)

        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, COLORS['border'], self.rect, width=1, border_radius=8)

        # Texte
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

class ModernSlider:
    def __init__(self, x, y, width, min_val, max_val, initial_val, label, unit=""):
        self.rect = pygame.Rect(x, y, width, 20)
        self.min_val = min_val
        self.max_val = max_val
        self.val = initial_val
        self.label = label
        self.unit = unit
        self.dragging = False
        self.font = pygame.font.SysFont("Arial", 14)
        self.label_font = pygame.font.SysFont("Arial", 12, bold=True)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                self.update_value(event.pos[0])
                return True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.update_value(event.pos[0])
            return True
        return False

    def update_value(self, mouse_x):
        relative_x = mouse_x - self.rect.x
        relative_x = max(0, min(self.rect.width, relative_x))
        self.val = self.min_val + (relative_x / self.rect.width) * (self.max_val - self.min_val)

    def draw(self, screen):
        # Label
        label_surface = self.label_font.render(self.label, True, COLORS['text'])
        screen.blit(label_surface, (self.rect.x, self.rect.y - 18))

        # Piste du slider
        track_rect = self.rect.copy()
        track_rect.height = 6
        track_rect.y += 7
        pygame.draw.rect(screen, COLORS['border'], track_rect, border_radius=3)

        # Partie active du slider
        active_width = int((self.val - self.min_val) / (self.max_val - self.min_val) * self.rect.width)
        active_rect = pygame.Rect(self.rect.x, track_rect.y, active_width, track_rect.height)
        pygame.draw.rect(screen, COLORS['primary'], active_rect, border_radius=3)

        # Curseur
        progress = (self.val - self.min_val) / (self.max_val - self.min_val)
        cursor_x = self.rect.x + progress * self.rect.width
        pygame.draw.circle(screen, COLORS['card'], (cursor_x, self.rect.y + 10), 12)
        pygame.draw.circle(screen, COLORS['primary'], (cursor_x, self.rect.y + 10), 10)
        pygame.draw.circle(screen, COLORS['border'], (cursor_x, self.rect.y + 10), 10, width=2)

        # Valeur
        value_text = f"{self.val:.1f}{self.unit}"
        value_surface = self.font.render(value_text, True, COLORS['text'])
        screen.blit(value_surface, (self.rect.x + self.rect.width + 10, self.rect.y + 3))

class ModernCard:
    def __init__(self, x, y, width, height, title=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.title = title
        self.title_font = pygame.font.SysFont("Arial", 18, bold=True)

    def draw(self, screen):
        # Ombre
        shadow_rect = self.rect.copy()
        shadow_rect.x += 3
        shadow_rect.y += 3
        pygame.draw.rect(screen, COLORS['shadow'], shadow_rect, border_radius=12)

        # Carte
        pygame.draw.rect(screen, COLORS['card'], self.rect, border_radius=12)
        pygame.draw.rect(screen, COLORS['border'], self.rect, width=1, border_radius=12)

        # Titre
        if self.title:
            title_surface = self.title_font.render(self.title, True, COLORS['text'])
            screen.blit(title_surface, (self.rect.x + 20, self.rect.y + 15))

            # Ligne sous le titre
            pygame.draw.line(screen, COLORS['border'],
                             (self.rect.x + 20, self.rect.y + 40),
                             (self.rect.right - 20, self.rect.y + 40), 1)

class ModernSelector:
    def __init__(self, x, y, width, options, selected_index=0, label=""):
        self.rect = pygame.Rect(x, y, width, 40)
        self.options = options
        self.selected_index = selected_index
        self.label = label
        self.font = pygame.font.SysFont("Arial", 14)
        self.label_font = pygame.font.SysFont("Arial", 12, bold=True)
        self.left_button = pygame.Rect(x + 10, y + 10, 20, 20)
        self.right_button = pygame.Rect(x + width - 30, y + 10, 20, 20)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.left_button.collidepoint(event.pos):
                self.selected_index = (self.selected_index - 1) % len(self.options)
                return True
            elif self.right_button.collidepoint(event.pos):
                self.selected_index = (self.selected_index + 1) % len(self.options)
                return True
        return False

    def draw(self, screen):
        # Label
        if self.label:
            label_surface = self.label_font.render(self.label, True, COLORS['text'])
            screen.blit(label_surface, (self.rect.x, self.rect.y - 18))

        # Fond du sélecteur
        pygame.draw.rect(screen, COLORS['card'], self.rect, border_radius=8)
        pygame.draw.rect(screen, COLORS['border'], self.rect, width=1, border_radius=8)

        # Boutons gauche/droite
        pygame.draw.rect(screen, COLORS['primary'], self.left_button, border_radius=4)
        pygame.draw.rect(screen, COLORS['primary'], self.right_button, border_radius=4)

        # Flèches
        left_arrow_font = pygame.font.SysFont("Arial", 20, bold=True)
        right_arrow_font = pygame.font.SysFont("Arial", 20, bold=True)

        left_arrow = left_arrow_font.render("<", True, (255, 255, 255))
        right_arrow = right_arrow_font.render(">", True, (255, 255, 255))

        left_rect = left_arrow.get_rect(center=self.left_button.center)
        right_rect = right_arrow.get_rect(center=self.right_button.center)

        screen.blit(left_arrow, left_rect)
        screen.blit(right_arrow, right_rect)

        # Texte de l'option sélectionnée
        if self.options:
            option_text = self.options[self.selected_index]["name"] if isinstance(self.options[self.selected_index], dict) else str(self.options[self.selected_index])
            text_surface = self.font.render(option_text, True, COLORS['text'])
            text_rect = text_surface.get_rect(center=self.rect.center)
            screen.blit(text_surface, text_rect)

# Variables globales
running = True
state = "config"  # États : "config" ou "simulation"

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

# Paramètres sélectionnés
selected_ball = 0
selected_ground = 0
selected_wind = 0
selected_height = 1
m = ball_types[selected_ball]["m"]
k = ball_types[selected_ball]["k"]
e = ground_types[selected_ground]["e"]
wind_speed = wind_speeds[selected_wind]
h0 = heights[selected_height]

# Variables de simulation
x = 0.0  # Position horizontale (m)
y = h0   # Position verticale (m)
vx = 0.0 # Vitesse horizontale (m/s)
vy = 0.0 # Vitesse verticale (m/s)
x_analytic = 0.0
y_analytic = h0
vx_analytic = 0.0
vy_analytic = 0.0
rebounds = 0
t = 0.0
paused = False
times = []
kinetic_energies = []
potential_energies = []
total_energies = []

def update_loop():
    global x, y, vx, vy, x_analytic, y_analytic, vx_analytic, vy_analytic, t, rebounds, paused
    if not running or paused:
        return

    # Solution numérique (Euler)
    F_gravity = -m * g
    F_friction_y = -k * vy
    F_wind = k * wind_speed  # Force horizontale due au vent
    ax = F_wind / m
    ay = (F_gravity + F_friction_y) / m
    vx += ax * dt
    vy += ay * dt
    x += vx * dt
    y += vy * dt

    # Solution analytique (sans frottement)
    ay_analytic = -g
    vy_analytic += ay_analytic * dt
    y_analytic += vy_analytic * dt
    x_analytic += vx_analytic * dt

    # Vérification du rebond (numérique)
    if y <= 0 and vy < 0:
        vy = -e * vy
        vx *= e  # Réduction de la vitesse horizontale
        y = 0
        rebounds += 1

    # Vérification du rebond (analytique)
    if y_analytic <= 0 and vy_analytic < 0:
        vy_analytic = -e * vy_analytic
        y_analytic = 0

    # Calcul des énergies
    kinetic_energy = 0.5 * m * (vx**2 + vy**2)
    potential_energy = m * g * y
    total_energy = kinetic_energy + potential_energy

    # Stockage pour le graphique
    times.append(t)
    kinetic_energies.append(kinetic_energy)
    potential_energies.append(potential_energy)
    total_energies.append(total_energy)

    # Limiter la taille des listes
    if len(times) > 200:
        times.pop(0)
        kinetic_energies.pop(0)
        potential_energies.pop(0)
        total_energies.pop(0)

    t += dt

def reset_simulation():
    global x, y, vx, vy, x_analytic, y_analytic, vx_analytic, vy_analytic, t, rebounds, times, kinetic_energies, potential_energies, total_energies
    x = 0.0
    y = h0
    vx = 0.0
    vy = 0.0
    x_analytic = 0.0
    y_analytic = h0
    vx_analytic = 0.0
    vy_analytic = 0.0
    t = 0.0
    rebounds = 0
    times = []
    kinetic_energies = []
    potential_energies = []
    total_energies = []

def draw_modern_header(screen, title):
    header_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 80)
    pygame.draw.rect(screen, COLORS['primary'], header_rect)

    # Titre principal
    title_font = pygame.font.SysFont("Arial", 28, bold=True)
    title_surface = title_font.render(title, True, (255, 255, 255))
    title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 40))
    screen.blit(title_surface, title_rect)

def draw_energy_graph(screen, graph_x, graph_y, graph_width, graph_height):
    max_energy = max(max(total_energies + [1.0]), m * g * h0)

    # Carte du graphique
    graph_card = ModernCard(graph_x, graph_y, graph_width, graph_height, "Évolution des Énergies")
    graph_card.draw(screen)

    # Grille intérieure
    for i in range(1, 5):
        y_line = graph_y + graph_height - 40 - i * (graph_height - 70) // 5
        x_line = graph_x + 50
        pygame.draw.line(screen, COLORS['grid'],
                         (x_line, y_line),
                         (graph_x + graph_width - 20, y_line), 1)

        # Valeur d'énergie
        energy_value = i * max_energy / 5
        value_text = pygame.font.SysFont("Arial", 10).render(f"{energy_value:.1f} J", True, COLORS['text_light'])
        screen.blit(value_text, (graph_x + 15, y_line - 5))

    # Axes du graphique
    pygame.draw.line(screen, COLORS['text'],
                     (graph_x + 50, graph_y + 50),
                     (graph_x + 50, graph_y + graph_height - 40), 2)
    pygame.draw.line(screen, COLORS['text'],
                     (graph_x + 50, graph_y + graph_height - 40),
                     (graph_x + graph_width - 20, graph_y + graph_height - 40), 2)

    # Légende
    legend_items = [
        (COLORS['danger'], "Énergie cinétique"),
        (COLORS['secondary'], "Énergie potentielle"),
        ((0, 123, 255), "Énergie totale")
    ]

    for i, (color, text) in enumerate(legend_items):
        pygame.draw.rect(screen, color, (graph_x + 70 + i*130, graph_y + 30, 12, 12))
        legend_text = pygame.font.SysFont("Arial", 12).render(text, True, COLORS['text'])
        screen.blit(legend_text, (graph_x + 85 + i*130, graph_y + 28))

    # Tracer les courbes d'énergie
    if len(times) > 1:
        # Surface pour dessiner les courbes avec anti-aliasing
        curve_surface = pygame.Surface((graph_width - 70, graph_height - 90), pygame.SRCALPHA)
        curve_surface.fill((0, 0, 0, 0))  # Transparent

        for i in range(1, len(times)):
            x1 = (i - 1) * (graph_width - 70) // 200
            x2 = i * (graph_width - 70) // 200

            # Calculer les positions Y normalisées
            y1_ke = (graph_height - 90) - int(kinetic_energies[i-1] / max_energy * (graph_height - 90))
            y2_ke = (graph_height - 90) - int(kinetic_energies[i] / max_energy * (graph_height - 90))

            y1_pe = (graph_height - 90) - int(potential_energies[i-1] / max_energy * (graph_height - 90))
            y2_pe = (graph_height - 90) - int(potential_energies[i] / max_energy * (graph_height - 90))

            y1_te = (graph_height - 90) - int(total_energies[i-1] / max_energy * (graph_height - 90))
            y2_te = (graph_height - 90) - int(total_energies[i] / max_energy * (graph_height - 90))

            # Dessiner avec anti-aliasing
            pygame.draw.aaline(curve_surface, COLORS['danger'], (x1, y1_ke), (x2, y2_ke))
            pygame.draw.aaline(curve_surface, COLORS['secondary'], (x1, y1_pe), (x2, y2_pe))
            pygame.draw.aaline(curve_surface, (0, 123, 255), (x1, y1_te), (x2, y2_te))

        # Appliquer la surface sur l'écran
        screen.blit(curve_surface, (graph_x + 50, graph_y + 50))

def draw_stats_panel(screen, x, y, width, height):
    stats_card = ModernCard(x, y, width, height, "Statistiques")
    stats_card.draw(screen)

    font = pygame.font.SysFont("Arial", 14)
    y_offset = 50

    stats = [
        ("Type de balle", ball_types[selected_ball]["name"]),
        ("Type de sol", ground_types[selected_ground]["name"]),
        ("Vent", f"{wind_speed} m/s"),
        ("Hauteur", f"{y:.2f} m"),
        ("Vitesse", f"{math.sqrt(vx**2 + vy**2):.2f} m/s"),
        ("Rebonds", str(rebounds)),
        ("Temps", f"{t:.2f} s"),
        ("Coefficient e", f"{e:.2f}"),
        ("Énergie cinétique", f"{0.5 * m * (vx**2 + vy**2):.2f} J"),
        ("Énergie potentielle", f"{m * g * y:.2f} J"),
        ("Énergie totale", f"{(0.5 * m * (vx**2 + vy**2) + m * g * y):.2f} J")
    ]

    for label, value in stats:
        label_text = font.render(label + ":", True, COLORS['text_light'])
        value_text = font.render(value, True, COLORS['text'])

        screen.blit(label_text, (x + 20, y + y_offset))
        screen.blit(value_text, (x + width - 20 - value_text.get_width(), y + y_offset))

        y_offset += 25

        # Ligne séparatrice fine
        if y_offset < height:
            pygame.draw.line(screen, COLORS['border'],
                             (x + 20, y + y_offset - 12),
                             (x + width - 20, y + y_offset - 12), 1)

def draw_simulation_area(screen, sim_x, sim_y, sim_width, sim_height):
    sim_card = ModernCard(sim_x, sim_y, sim_width, sim_height, "Zone de Simulation")
    sim_card.draw(screen)

    # Dessin du sol
    ground_y = sim_y + sim_height - 50
    pygame.draw.line(screen, COLORS['text'],
                     (sim_x + 20, ground_y),
                     (sim_x + sim_width - 20, ground_y), 3)

    # Effet d'ombre pour le sol
    for i in range(1, 4):
        alpha = 100 - i * 20
        pygame.draw.line(screen, (COLORS['text'][0], COLORS['text'][1], COLORS['text'][2], alpha),
                         (sim_x + 20, ground_y + i),
                         (sim_x + sim_width - 20, ground_y + i), 1)

    # Grille verticale
    origin_x = sim_x + 100
    for i in range(0, int((sim_width - 120) / SCALE) + 1):
        x_grid = origin_x + i * SCALE
        pygame.draw.line(screen, COLORS['grid'],
                         (x_grid, sim_y + 50),
                         (x_grid, ground_y), 1)

        meter_text = pygame.font.SysFont("Arial", 10).render(f"{i}m", True, COLORS['text_light'])
        screen.blit(meter_text, (x_grid - 5, ground_y + 5))

    # Grille horizontale et échelle de hauteur
    for i in range(0, int(h0) + 2):
        y_grid = ground_y - i * SCALE
        if y_grid > sim_y + 50:  # Ne pas dépasser le haut de la zone
            pygame.draw.line(screen, COLORS['grid'],
                             (sim_x + 20, y_grid),
                             (sim_x + sim_width - 20, y_grid), 1)

            height_text = pygame.font.SysFont("Arial", 10).render(f"{i}m", True, COLORS['text_light'])
            screen.blit(height_text, (sim_x + 5, y_grid - 5))

    # Dessin des balles avec ombre
    ball_offset_x = origin_x
    pixel_x = ball_offset_x + int(x * SCALE)
    pixel_y = ground_y - int(y * SCALE)
    pixel_x_analytic = ball_offset_x + int(x_analytic * SCALE)
    pixel_y_analytic = ground_y - int(y_analytic * SCALE)

    # Ombres des balles sur le sol
    shadow_radius = max(3, BALL_RADIUS - int(y * 2))
    pygame.draw.ellipse(screen, (0, 0, 0, 50),
                        (pixel_x - shadow_radius, ground_y - 3, shadow_radius * 2, 6))

    shadow_radius_analytic = max(3, BALL_RADIUS - int(y_analytic * 2))
    pygame.draw.ellipse(screen, (0, 0, 0, 30),
                        (pixel_x_analytic - shadow_radius_analytic, ground_y - 3, shadow_radius_analytic * 2, 6))

    # Balle avec effet (numérique)
    pygame.gfxdraw.filled_circle(screen, pixel_x, pixel_y, BALL_RADIUS, COLORS['ball1'])
    pygame.gfxdraw.aacircle(screen, pixel_x, pixel_y, BALL_RADIUS, COLORS['ball1'])  # Anti-aliasing
    # Effet de brillance
    pygame.gfxdraw.filled_circle(screen, pixel_x - 3, pixel_y - 3, 3, (255, 255, 255, 150))

    # Balle analytique
    pygame.gfxdraw.filled_circle(screen, pixel_x_analytic, pixel_y_analytic, BALL_RADIUS, COLORS['ball2'])
    pygame.gfxdraw.aacircle(screen, pixel_x_analytic, pixel_y_analytic, BALL_RADIUS, COLORS['ball2'])
    pygame.gfxdraw.filled_circle(screen, pixel_x_analytic - 3, pixel_y_analytic - 3, 3, (255, 255, 255, 150))

    # Légende des balles
    legend_y = sim_y + sim_height - 30

    pygame.gfxdraw.filled_circle(screen, sim_x + 40, legend_y, 6, COLORS['ball1'])
    ball1_text = pygame.font.SysFont("Arial", 12).render("Numérique (avec frottement)", True, COLORS['text'])
    screen.blit(ball1_text, (sim_x + 50, legend_y - 6))

    pygame.gfxdraw.filled_circle(screen, sim_x + sim_width // 2, legend_y, 6, COLORS['ball2'])
    ball2_text = pygame.font.SysFont("Arial", 12).render("Analytique (sans frottement)", True, COLORS['text'])
    screen.blit(ball2_text, (sim_x + sim_width // 2 + 10, legend_y - 6))

def draw_config_screen():
    global selected_ball, selected_ground, selected_wind, selected_height, m, k, e, wind_speed, h0

    dt = clock.tick(60) / 1000.0
    mouse_pos = pygame.mouse.get_pos()

    # Fond et en-tête
    screen.fill(COLORS['background'])
    draw_modern_header(screen, "Configuration de la Simulation")

    # Carte principale du panneau de configuration
    main_card = ModernCard(50, 100, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 170)
    main_card.draw(screen)

    # Mise en page en colonnes
    col1_x = 80
    col2_x = SCREEN_WIDTH // 2 + 30
    y_start = 150

    # Carte de configuration de la balle
    ball_card = ModernCard(col1_x, y_start, 500, 200, "Propriétés du Projectile")
    ball_card.draw(screen)

    # Sélecteurs pour les propriétés de la balle
    ball_selector = ModernSelector(col1_x + 20, y_start + 70, 460, ball_types, selected_ball, "Type de balle")
    ball_selector.draw(screen)

    # Infos sur la balle sélectionnée
    info_y = y_start + 130
    info_font = pygame.font.SysFont("Arial", 14)

    ball_props = [
        ("Masse", f"{ball_types[selected_ball]['m']:.3f} kg"),
        ("Coefficient d'air", f"{ball_types[selected_ball]['k']:.3f}")
    ]

    for i, (label, value) in enumerate(ball_props):
        label_text = info_font.render(label + ":", True, COLORS['text_light'])
        value_text = info_font.render(value, True, COLORS['text'])

        screen.blit(label_text, (col1_x + 50, info_y + i * 30))
        screen.blit(value_text, (col1_x + 350, info_y + i * 30))

    # Carte pour les conditions environnementales
    env_card = ModernCard(col1_x, y_start + 220, 500, 250, "Conditions Environnementales")
    env_card.draw(screen)

    # Sélecteurs pour le sol, le vent et la hauteur
    ground_selector = ModernSelector(col1_x + 20, y_start + 290, 460, ground_types, selected_ground, "Type de sol")
    wind_selector = ModernSelector(col1_x + 20, y_start + 360, 460, [f"{w} m/s" for w in wind_speeds], selected_wind, "Vitesse du vent")
    height_selector = ModernSelector(col1_x + 20, y_start + 430, 460, [f"{h} m" for h in heights], selected_height, "Hauteur initiale")

    ground_selector.draw(screen)
    wind_selector.draw(screen)
    height_selector.draw(screen)

    # Prévisualisation de la simulation
    preview_card = ModernCard(col2_x, y_start, 500, 470, "Prévisualisation")
    preview_card.draw(screen)

    # Dessiner une petite zone de prévisualisation
    preview_x = col2_x + 50
    preview_y = y_start + 70
    preview_width = 400
    preview_height = 300

    # Sol
    ground_y = preview_y + preview_height - 50
    pygame.draw.line(screen, COLORS['text'], (preview_x, ground_y), (preview_x + preview_width, ground_y), 2)

    # Balle statique à la hauteur initiale
    static_ball_x = preview_x + preview_width // 2
    static_ball_y = ground_y - int(heights[selected_height] * 15)  # Échelle réduite pour la prévisualisation

    # Dessiner une ligne pointillée pour la hauteur
    for i in range(0, int(static_ball_y - ground_y), -10):
        pygame.draw.line(screen, COLORS['grid'],
                         (static_ball_x - 5, ground_y + i),
                         (static_ball_x + 5, ground_y + i), 1)

    # Type de sol (texture)
    sol_text = pygame.font.SysFont("Arial", 14).render(f"Sol: {ground_types[selected_ground]['name']}", True, COLORS['text'])
    screen.blit(sol_text, (preview_x + 10, ground_y + 10))

    # Dessin de la balle
    pygame.gfxdraw.filled_circle(screen, static_ball_x, static_ball_y, 15, COLORS['ball1'])
    pygame.gfxdraw.aacircle(screen, static_ball_x, static_ball_y, 15, COLORS['ball1'])
    pygame.gfxdraw.filled_circle(screen, static_ball_x - 4, static_ball_y - 4, 4, (255, 255, 255, 150))

    # Indication de la hauteur
    height_text = pygame.font.SysFont("Arial", 12).render(f"Hauteur: {heights[selected_height]} m", True, COLORS['text'])
    screen.blit(height_text, (static_ball_x + 20, static_ball_y))

    # Flèche pour le vent si non nul
    if wind_speeds[selected_wind] > 0:
        wind_length = wind_speeds[selected_wind] * 5
        wind_y = static_ball_y - 40
        pygame.draw.line(screen, COLORS['primary'],
                         (static_ball_x - wind_length, wind_y),
                         (static_ball_x, wind_y), 2)
        # Triangle de pointe de flèche
        pygame.draw.polygon(screen, COLORS['primary'], [
            (static_ball_x, wind_y - 5),
            (static_ball_x, wind_y + 5),
            (static_ball_x + 10, wind_y)
        ])
        # Texte pour le vent
        wind_text = pygame.font.SysFont("Arial", 12).render(f"Vent: {wind_speeds[selected_wind]} m/s", True, COLORS['primary'])
        screen.blit(wind_text, (static_ball_x - wind_length - 120, wind_y - 6))

    # Bouton pour lancer la simulation
    start_button = ModernButton(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 50, 200, 50, "Lancer la Simulation", 'secondary', 20)
    start_button.update(mouse_pos, dt)
    start_button.draw(screen)

    pygame.display.flip()

    # Retourner les éléments interactifs
    return start_button, ball_selector, ground_selector, wind_selector, height_selector

def draw_simulation_screen():
    global e, h0, paused

    dt = clock.tick(60) / 1000.0
    mouse_pos = pygame.mouse.get_pos()

    # Fond
    screen.fill(COLORS['background'])

    # En-tête avec contrôles
    header_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 80)
    pygame.draw.rect(screen, COLORS['primary'], header_rect)

    # Titre
    title_font = pygame.font.SysFont("Arial", 24, bold=True)
    title_surface = title_font.render("Simulation de Chute Libre", True, (255, 255, 255))
    screen.blit(title_surface, (20, 25))

    # Boutons de contrôle
    pause_text = "Reprendre" if paused else "Pause"
    pause_button = ModernButton(SCREEN_WIDTH - 430, 15, 120, 50, pause_text, 'warning', 16)
    reset_button = ModernButton(SCREEN_WIDTH - 300, 15, 120, 50, "Réinitialiser", 'danger', 16)
    config_button = ModernButton(SCREEN_WIDTH - 170, 15, 150, 50, "Configuration", 'secondary', 16)

    pause_button.update(mouse_pos, dt)
    reset_button.update(mouse_pos, dt)
    config_button.update(mouse_pos, dt)

    pause_button.draw(screen)
    reset_button.draw(screen)
    config_button.draw(screen)

    # Disposition principale
    left_panel_width = 800
    right_panel_width = 380

    # Zone de simulation à gauche
    draw_simulation_area(screen, 20, 100, left_panel_width, 400)

    # Graphique d'énergie en bas à gauche
    draw_energy_graph(screen, 20, 520, left_panel_width, 260)

    # Panneau de contrôle à droite
    control_card = ModernCard(SCREEN_WIDTH - right_panel_width - 20, 100, right_panel_width, 300, "Contrôles")
    control_card.draw(screen)

    # Sliders de contrôle
    slider_x = SCREEN_WIDTH - right_panel_width
    slider_y = 170
    slider_spacing = 80

    e_slider = ModernSlider(slider_x, slider_y, right_panel_width - 120, 0.1, 1.0, e, "Coefficient de restitution (e)")
    e_slider.draw(screen)

    h0_slider = ModernSlider(slider_x, slider_y + slider_spacing, right_panel_width - 120, 1.0, 20.0, h0, "Hauteur initiale", " m")
    h0_slider.draw(screen)

    # Panneau de statistiques
    draw_stats_panel(screen, SCREEN_WIDTH - right_panel_width - 20, 420, right_panel_width, 360)

    pygame.display.flip()

    return pause_button, reset_button, config_button, e_slider, h0_slider

async def main():
    global running, paused, state, selected_ball, selected_ground, selected_wind, selected_height
    global m, k, e, wind_speed, h0

    while running:
        if state == "config":
            ui_elements = draw_config_screen()
            start_button, ball_selector, ground_selector, wind_selector, height_selector = ui_elements

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos

                    if start_button.rect.collidepoint(pos):
                        start_button.click()
                        state = "simulation"
                        reset_simulation()

                    # Gérer les sélecteurs
                    if ball_selector.handle_event(event):
                        selected_ball = ball_selector.selected_index
                        m = ball_types[selected_ball]["m"]
                        k = ball_types[selected_ball]["k"]

                    if ground_selector.handle_event(event):
                        selected_ground = ground_selector.selected_index
                        e = ground_types[selected_ground]["e"]

                    if wind_selector.handle_event(event):
                        selected_wind = wind_selector.selected_index
                        wind_speed = wind_speeds[selected_wind]

                    if height_selector.handle_event(event):
                        selected_height = height_selector.selected_index
                        h0 = heights[selected_height]

        else:  # state == "simulation"
            if not paused:
                update_loop()

            ui_elements = draw_simulation_screen()
            pause_button, reset_button, config_button, e_slider, h0_slider = ui_elements

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos

                    if pause_button.rect.collidepoint(pos):
                        pause_button.click()
                        paused = not paused

                    elif reset_button.rect.collidepoint(pos):
                        reset_button.click()
                        reset_simulation()

                    elif config_button.rect.collidepoint(pos):
                        config_button.click()
                        state = "config"

                # Gestion des sliders
                if e_slider.handle_event(event):
                    e = e_slider.val

                if h0_slider.handle_event(event):
                    old_h0 = h0
                    h0 = h0_slider.val
                    if old_h0 != h0:
                        reset_simulation()

        await asyncio.sleep(1.0 / FPS)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())