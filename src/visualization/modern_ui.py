"""Interface utilisateur moderne pour la simulation de chute libre"""

import asyncio
import platform
import pygame
import pygame.gfxdraw
import math
from typing import List, Dict, Optional, Tuple

class ModernColors:
    """Palette de couleurs moderne"""
    PRIMARY = (70, 130, 180)
    PRIMARY_HOVER = (100, 149, 237)
    SECONDARY = (60, 179, 113)
    SECONDARY_HOVER = (85, 195, 135)
    DANGER = (220, 53, 69)
    DANGER_HOVER = (225, 75, 85)
    WARNING = (255, 193, 7)
    WARNING_HOVER = (255, 210, 50)
    BACKGROUND = (248, 249, 250)
    CARD = (255, 255, 255)
    TEXT = (52, 58, 64)
    TEXT_LIGHT = (108, 117, 125)
    BORDER = (206, 212, 218)
    SHADOW = (0, 0, 0, 30)
    BALL1 = (220, 53, 69)
    BALL2 = (0, 123, 255)
    GRID = (230, 234, 238)

class ModernButton:
    """Bouton moderne avec effets visuels"""

    def __init__(self, x: int, y: int, width: int, height: int, text: str,
                 color_scheme: str = 'primary', font_size: int = 16):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color_scheme = color_scheme
        self.font = pygame.font.SysFont("Arial", font_size, bold=True)
        self.is_hovered = False
        self.click_effect = 0.0

    def update(self, mouse_pos: Tuple[int, int], dt: float):
        """Met à jour l'état du bouton"""
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        if self.click_effect > 0:
            self.click_effect = max(0, self.click_effect - dt * 5)

    def click(self):
        """Active l'effet de clic"""
        self.click_effect = 1.0

    def draw(self, screen: pygame.Surface):
        """Dessine le bouton"""
        # Ombre
        shadow_rect = self.rect.copy()
        shadow_rect.x += 2
        shadow_rect.y += 2
        pygame.draw.rect(screen, ModernColors.SHADOW, shadow_rect, border_radius=8)

        # Couleur selon l'état
        if self.color_scheme == 'primary':
            color = ModernColors.PRIMARY_HOVER if self.is_hovered else ModernColors.PRIMARY
        elif self.color_scheme == 'secondary':
            color = ModernColors.SECONDARY_HOVER if self.is_hovered else ModernColors.SECONDARY
        elif self.color_scheme == 'danger':
            color = ModernColors.DANGER_HOVER if self.is_hovered else ModernColors.DANGER
        elif self.color_scheme == 'warning':
            color = ModernColors.WARNING_HOVER if self.is_hovered else ModernColors.WARNING
        else:
            color = ModernColors.PRIMARY

        # Effet de clic
        if self.click_effect > 0:
            brightness = 1 - self.click_effect * 0.2
            color = tuple(int(c * brightness) for c in color)

        # Bouton principal
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, ModernColors.BORDER, self.rect, width=1, border_radius=8)

        # Texte
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

class ModernSlider:
    """Slider moderne avec libellé et valeur"""

    def __init__(self, x: int, y: int, width: int, min_val: float, max_val: float,
                 initial_val: float, label: str, unit: str = ""):
        self.rect = pygame.Rect(x, y, width, 20)
        self.min_val = min_val
        self.max_val = max_val
        self.val = initial_val
        self.label = label
        self.unit = unit
        self.dragging = False
        self.font = pygame.font.SysFont("Arial", 14)
        self.label_font = pygame.font.SysFont("Arial", 12, bold=True)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Gère les événements du slider"""
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

    def update_value(self, mouse_x: int):
        """Met à jour la valeur selon la position de la souris"""
        relative_x = mouse_x - self.rect.x
        relative_x = max(0, min(self.rect.width, relative_x))
        self.val = self.min_val + (relative_x / self.rect.width) * (self.max_val - self.min_val)

    def draw(self, screen: pygame.Surface):
        """Dessine le slider"""
        # Label
        label_surface = self.label_font.render(self.label, True, ModernColors.TEXT)
        screen.blit(label_surface, (self.rect.x, self.rect.y - 18))

        # Piste
        track_rect = self.rect.copy()
        track_rect.height = 6
        track_rect.y += 7
        pygame.draw.rect(screen, ModernColors.BORDER, track_rect, border_radius=3)

        # Partie active
        progress = (self.val - self.min_val) / (self.max_val - self.min_val)
        active_width = int(progress * self.rect.width)
        active_rect = pygame.Rect(self.rect.x, track_rect.y, active_width, track_rect.height)
        pygame.draw.rect(screen, ModernColors.PRIMARY, active_rect, border_radius=3)

        # Curseur
        cursor_x = self.rect.x + progress * self.rect.width
        pygame.draw.circle(screen, ModernColors.CARD, (int(cursor_x), self.rect.y + 10), 12)
        pygame.draw.circle(screen, ModernColors.PRIMARY, (int(cursor_x), self.rect.y + 10), 10)
        pygame.draw.circle(screen, ModernColors.BORDER, (int(cursor_x), self.rect.y + 10), 10, width=2)

        # Valeur
        value_text = f"{self.val:.1f}{self.unit}"
        value_surface = self.font.render(value_text, True, ModernColors.TEXT)
        screen.blit(value_surface, (self.rect.x + self.rect.width + 10, self.rect.y + 3))

class ModernCard:
    """Carte moderne avec ombre et titre"""

    def __init__(self, x: int, y: int, width: int, height: int, title: Optional[str] = None):
        self.rect = pygame.Rect(x, y, width, height)
        self.title = title
        self.title_font = pygame.font.SysFont("Arial", 18, bold=True)

    def draw(self, screen: pygame.Surface):
        """Dessine la carte"""
        # Ombre
        shadow_rect = self.rect.copy()
        shadow_rect.x += 3
        shadow_rect.y += 3
        pygame.draw.rect(screen, ModernColors.SHADOW, shadow_rect, border_radius=12)

        # Carte
        pygame.draw.rect(screen, ModernColors.CARD, self.rect, border_radius=12)
        pygame.draw.rect(screen, ModernColors.BORDER, self.rect, width=1, border_radius=12)

        # Titre
        if self.title:
            title_surface = self.title_font.render(self.title, True, ModernColors.TEXT)
            screen.blit(title_surface, (self.rect.x + 20, self.rect.y + 15))

            # Ligne sous le titre
            pygame.draw.line(screen, ModernColors.BORDER,
                             (self.rect.x + 20, self.rect.y + 40),
                             (self.rect.right - 20, self.rect.y + 40), 1)

class ModernSelector:
    """Sélecteur moderne avec flèches"""

    def __init__(self, x: int, y: int, width: int, options: List, selected_index: int = 0, label: str = ""):
        self.rect = pygame.Rect(x, y, width, 40)
        self.options = options
        self.selected_index = selected_index
        self.label = label
        self.font = pygame.font.SysFont("Arial", 14)
        self.label_font = pygame.font.SysFont("Arial", 12, bold=True)
        self.left_button = pygame.Rect(x + 10, y + 10, 20, 20)
        self.right_button = pygame.Rect(x + width - 30, y + 10, 20, 20)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Gère les événements du sélecteur"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.left_button.collidepoint(event.pos):
                self.selected_index = (self.selected_index - 1) % len(self.options)
                return True
            elif self.right_button.collidepoint(event.pos):
                self.selected_index = (self.selected_index + 1) % len(self.options)
                return True
        return False

    def draw(self, screen: pygame.Surface):
        """Dessine le sélecteur"""
        # Label
        if self.label:
            label_surface = self.label_font.render(self.label, True, ModernColors.TEXT)
            screen.blit(label_surface, (self.rect.x, self.rect.y - 18))

        # Fond
        pygame.draw.rect(screen, ModernColors.CARD, self.rect, border_radius=8)
        pygame.draw.rect(screen, ModernColors.BORDER, self.rect, width=1, border_radius=8)

        # Boutons
        pygame.draw.rect(screen, ModernColors.PRIMARY, self.left_button, border_radius=4)
        pygame.draw.rect(screen, ModernColors.PRIMARY, self.right_button, border_radius=4)

        # Flèches
        left_arrow = pygame.font.SysFont("Arial", 20, bold=True).render("<", True, (255, 255, 255))
        right_arrow = pygame.font.SysFont("Arial", 20, bold=True).render(">", True, (255, 255, 255))

        left_rect = left_arrow.get_rect(center=self.left_button.center)
        right_rect = right_arrow.get_rect(center=self.right_button.center)

        screen.blit(left_arrow, left_rect)
        screen.blit(right_arrow, right_rect)

        # Texte de l'option
        if self.options:
            option_text = self.options[self.selected_index]["name"] if isinstance(self.options[self.selected_index], dict) else str(self.options[self.selected_index])
            text_surface = self.font.render(option_text, True, ModernColors.TEXT)
            text_rect = text_surface.get_rect(center=self.rect.center)
            screen.blit(text_surface, text_rect)