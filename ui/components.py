import pygame
import pygame.gfxdraw
from config import COLORS

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