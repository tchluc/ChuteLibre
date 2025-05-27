import pygame
from config import (
    COLORS, SCREEN_WIDTH, SCREEN_HEIGHT,
    ball_types, ground_types, wind_speeds, heights
)
from ui.components import ModernButton, ModernSelector, ModernCard
from ui.utils import draw_modern_header

def draw_config_screen(screen, clock, selected_params):
    """Dessine l'écran de configuration"""
    selected_ball, selected_ground, selected_wind, selected_height = selected_params

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
    return {
        'start_button': start_button,
        'ball_selector': ball_selector,
        'ground_selector': ground_selector,
        'wind_selector': wind_selector,
        'height_selector': height_selector
    }