import asyncio
import platform
import pygame
import sys

# Importation des modules
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from physics import PhysicsEngine
from data.simulation_data import SimulationData
from ui.config_screen import draw_config_screen
from ui.simulation_screen import draw_simulation_screen

# Initialisation de Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Chute Libre - Configuration")
clock = pygame.time.Clock()

# Variables d'état
running = True
state = "config"  # États : "config" ou "simulation"
paused = False

# Initialisation des données et du moteur physique
sim_data = SimulationData()
physics_engine = None  # Sera créé lors du passage en mode simulation

async def main():
    global running, paused, state, physics_engine

    while running:
        if state == "config":
            # Affichage de l'écran de configuration
            ui_elements = draw_config_screen(screen, clock, sim_data.get_selection_tuple())

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos

                    if ui_elements['start_button'].rect.collidepoint(pos):
                        ui_elements['start_button'].click()

                        # Mise à jour des paramètres de la simulation
                        sim_data.update_derived_values()

                        # Création du moteur physique
                        params = sim_data.get_physics_parameters()
                        physics_engine = PhysicsEngine(
                            params['m'], params['k'], params['e'],
                            params['wind_speed'], params['h0']
                        )
                        physics_engine.selected_ball = params['selected_ball']
                        physics_engine.selected_ground = params['selected_ground']

                        # Passage à l'écran de simulation
                        state = "simulation"
                        pygame.display.set_caption("Chute Libre - Simulation")

                    # Gestion des sélecteurs
                    if ui_elements['ball_selector'].handle_event(event):
                        sim_data.selected_ball = ui_elements['ball_selector'].selected_index
                        sim_data.update_derived_values()

                    if ui_elements['ground_selector'].handle_event(event):
                        sim_data.selected_ground = ui_elements['ground_selector'].selected_index
                        sim_data.update_derived_values()

                    if ui_elements['wind_selector'].handle_event(event):
                        sim_data.selected_wind = ui_elements['wind_selector'].selected_index
                        sim_data.update_derived_values()

                    if ui_elements['height_selector'].handle_event(event):
                        sim_data.selected_height = ui_elements['height_selector'].selected_index
                        sim_data.update_derived_values()

        else:  # state == "simulation"
            # Mise à jour de la physique
            physics_engine.update(paused)

            # Affichage de l'écran de simulation
            ui_elements = draw_simulation_screen(screen, clock, physics_engine, paused)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos

                    if ui_elements['pause_button'].rect.collidepoint(pos):
                        ui_elements['pause_button'].click()
                        paused = not paused

                    elif ui_elements['reset_button'].rect.collidepoint(pos):
                        ui_elements['reset_button'].click()
                        physics_engine.reset()

                    elif ui_elements['config_button'].rect.collidepoint(pos):
                        ui_elements['config_button'].click()
                        state = "config"
                        pygame.display.set_caption("Chute Libre - Configuration")

                # Gestion des sliders
                if ui_elements['e_slider'].handle_event(event):
                    physics_engine.update_parameters(e=ui_elements['e_slider'].val)

                if ui_elements['h0_slider'].handle_event(event):
                    physics_engine.update_parameters(h0=ui_elements['h0_slider'].val)

        await asyncio.sleep(1.0 / FPS)

if __name__ == "__main__":
    if platform.system() == "Emscripten":
        asyncio.ensure_future(main())
    else:
        asyncio.run(main())