import pygame
from config import COLORS, SCREEN_WIDTH

def draw_modern_header(screen, title):
    """Dessine l'en-tête de l'application"""
    header_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 80)
    pygame.draw.rect(screen, COLORS['primary'], header_rect)

    # Titre principal
    title_font = pygame.font.SysFont("Arial", 28, bold=True)
    title_surface = title_font.render(title, True, (255, 255, 255))
    title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 40))
    screen.blit(title_surface, title_rect)

def draw_stats_panel(screen, x, y, width, height, physics_engine):
    """Dessine le panneau de statistiques"""
    from ui.components import ModernCard

    stats_card = ModernCard(x, y, width, height, "Statistiques")
    stats_card.draw(screen)

    font = pygame.font.SysFont("Arial", 14)
    y_offset = 50

    from math import sqrt
    from config import g, ball_types, ground_types, wind_speeds

    stats = [
        ("Type de balle", ball_types[physics_engine.selected_ball]["name"]),
        ("Type de sol", ground_types[physics_engine.selected_ground]["name"]),
        ("Vent", f"{physics_engine.wind_speed} m/s"),
        ("Hauteur", f"{physics_engine.y:.2f} m"),
        ("Vitesse", f"{sqrt(physics_engine.vx**2 + physics_engine.vy**2):.2f} m/s"),
        ("Rebonds", str(physics_engine.rebounds)),
        ("Temps", f"{physics_engine.t:.2f} s"),
        ("Coefficient e", f"{physics_engine.e:.2f}"),
        ("Énergie cinétique", f"{0.5 * physics_engine.m * (physics_engine.vx**2 + physics_engine.vy**2):.2f} J"),
        ("Énergie potentielle", f"{physics_engine.m * g * physics_engine.y:.2f} J"),
        ("Énergie totale", f"{(0.5 * physics_engine.m * (physics_engine.vx**2 + physics_engine.vy**2) + physics_engine.m * g * physics_engine.y):.2f} J")
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