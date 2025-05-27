import pygame
import pygame.gfxdraw
import math
from config import (
    COLORS, SCREEN_WIDTH, SCREEN_HEIGHT,
    GROUND_Y, BALL_RADIUS, SCALE, g
)
from ui.components import ModernButton, ModernSlider, ModernCard
from ui.utils import draw_stats_panel

def draw_energy_graph(screen, graph_x, graph_y, graph_width, graph_height, physics_engine):
    """Dessine le graphique d'énergie"""
    max_energy = max(max(physics_engine.total_energies + [1.0]), physics_engine.m * g * physics_engine.h0)

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
    if len(physics_engine.times) > 1:
        # Surface pour dessiner les courbes avec anti-aliasing
        curve_surface = pygame.Surface((graph_width - 70, graph_height - 90), pygame.SRCALPHA)
        curve_surface.fill((0, 0, 0, 0))  # Transparent

        for i in range(1, len(physics_engine.times)):
            x1 = (i - 1) * (graph_width - 70) // 200
            x2 = i * (graph_width - 70) // 200

            # Calculer les positions Y normalisées
            y1_ke = (graph_height - 90) - int(physics_engine.kinetic_energies[i-1] / max_energy * (graph_height - 90))
            y2_ke = (graph_height - 90) - int(physics_engine.kinetic_energies[i] / max_energy * (graph_height - 90))

            y1_pe = (graph_height - 90) - int(physics_engine.potential_energies[i-1] / max_energy * (graph_height - 90))
            y2_pe = (graph_height - 90) - int(physics_engine.potential_energies[i] / max_energy * (graph_height - 90))

            y1_te = (graph_height - 90) - int(physics_engine.total_energies[i-1] / max_energy * (graph_height - 90))
            y2_te = (graph_height - 90) - int(physics_engine.total_energies[i] / max_energy * (graph_height - 90))

            # Dessiner avec anti-aliasing
            pygame.draw.aaline(curve_surface, COLORS['danger'], (x1, y1_ke), (x2, y2_ke))
            pygame.draw.aaline(curve_surface, COLORS['secondary'], (x1, y1_pe), (x2, y2_pe))
            pygame.draw.aaline(curve_surface, (0, 123, 255), (x1, y1_te), (x2, y2_te))

        # Appliquer la surface sur l'écran
        screen.blit(curve_surface, (graph_x + 50, graph_y + 50))

def draw_simulation_area(screen, sim_x, sim_y, sim_width, sim_height, physics_engine):
    """Dessine la zone de simulation avec la balle et le sol"""
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
    for i in range(0, int(physics_engine.h0) + 2):
        y_grid = ground_y - i * SCALE
        if y_grid > sim_y + 50:  # Ne pas dépasser le haut de la zone
            pygame.draw.line(screen, COLORS['grid'],
                             (sim_x + 20, y_grid),
                             (sim_x + sim_width - 20, y_grid), 1)

            height_text = pygame.font.SysFont("Arial", 10).render(f"{i}m", True, COLORS['text_light'])
            screen.blit(height_text, (sim_x + 5, y_grid - 5))

    # Dessin des balles avec ombre
    ball_offset_x = origin_x
    pixel_x = ball_offset_x + int(physics_engine.x * SCALE)
    pixel_y = ground_y - int(physics_engine.y * SCALE)
    pixel_x_analytic = ball_offset_x + int(physics_engine.x_analytic * SCALE)
    pixel_y_analytic = ground_y - int(physics_engine.y_analytic * SCALE)

    # Ombres des balles sur le sol
    shadow_radius = max(3, BALL_RADIUS - int(physics_engine.y * 2))
    pygame.draw.ellipse(screen, (0, 0, 0, 50),
                        (pixel_x - shadow_radius, ground_y - 3, shadow_radius * 2, 6))

    shadow_radius_analytic = max(3, BALL_RADIUS - int(physics_engine.y_analytic * 2))
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

def draw_simulation_screen(screen, clock, physics_engine, paused):
    """Dessine l'écran de simulation"""
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
    draw_simulation_area(screen, 20, 100, left_panel_width, 400, physics_engine)

    # Graphique d'énergie en bas à gauche
    draw_energy_graph(screen, 20, 520, left_panel_width, 260, physics_engine)

    # Panneau de contrôle à droite
    control_card = ModernCard(SCREEN_WIDTH - right_panel_width - 20, 100, right_panel_width, 300, "Contrôles")
    control_card.draw(screen)

    # Sliders de contrôle
    slider_x = SCREEN_WIDTH - right_panel_width
    slider_y = 170
    slider_spacing = 80

    e_slider = ModernSlider(slider_x, slider_y, right_panel_width - 120, 0.1, 1.0, physics_engine.e, "Coefficient de restitution (e)")
    e_slider.draw(screen)

    h0_slider = ModernSlider(slider_x, slider_y + slider_spacing, right_panel_width - 120, 1.0, 20.0, physics_engine.h0, "Hauteur initiale", " m")
    h0_slider.draw(screen)

    # Panneau de statistiques
    draw_stats_panel(screen, SCREEN_WIDTH - right_panel_width - 20, 420, right_panel_width, 360, physics_engine)

    pygame.display.flip()

    return {
        'pause_button': pause_button,
        'reset_button': reset_button,
        'config_button': config_button,
        'e_slider': e_slider,
        'h0_slider': h0_slider
    }