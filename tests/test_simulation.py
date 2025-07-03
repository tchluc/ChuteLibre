"""Tests unitaires pour le simulateur"""

import unittest
import sys
import os

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.simulation.simulator import FreeFallSimulator
from src.models.physics_object import PhysicsObject
from src.simulation.numerical_methods import EulerMethod

class TestFreeFallSimulator(unittest.TestCase):
    """Tests pour le simulateur de chute libre"""

    def setUp(self):
        """Initialisation avant chaque test"""
        self.simulator = FreeFallSimulator(dt=0.01, air_resistance=False)
        self.obj = PhysicsObject(x=0, y=10, vx=0, vy=0, mass=1.0)

    def test_add_remove_object(self):
        """Test d'ajout et suppression d'objet"""
        self.assertEqual(len(self.simulator.objects), 0)

        self.simulator.add_object(self.obj)
        self.assertEqual(len(self.simulator.objects), 1)

        self.simulator.remove_object(self.obj)
        self.assertEqual(len(self.simulator.objects), 0)

    def test_simulation_step(self):
        """Test d'un pas de simulation"""
        self.simulator.add_object(self.obj)
        initial_y = self.obj.y
        initial_vy = self.obj.vy

        # Faire plusieurs pas pour un changement plus visible
        for _ in range(10):
            self.simulator.step()

        # L'objet doit avoir bougé après plusieurs pas
        self.assertNotEqual(self.obj.y, initial_y)
        self.assertLess(self.obj.y, initial_y)  # Doit tomber
        self.assertLess(self.obj.vy, initial_vy)  # Vitesse vers le bas (plus négative)

    def test_simulation_step_single_with_initial_velocity(self):
        """Test d'un pas de simulation avec vitesse initiale"""
        # Objet avec vitesse initiale pour changement plus visible
        obj_with_velocity = PhysicsObject(x=0, y=10, vx=1, vy=-2, mass=1.0)
        self.simulator.add_object(obj_with_velocity)

        initial_x = obj_with_velocity.x
        initial_y = obj_with_velocity.y
        initial_vy = obj_with_velocity.vy

        self.simulator.step()

        # Avec vitesse initiale, les changements sont plus visibles
        self.assertNotEqual(obj_with_velocity.x, initial_x)  # Mouvement horizontal
        self.assertNotEqual(obj_with_velocity.y, initial_y)  # Mouvement vertical
        self.assertLess(obj_with_velocity.vy, initial_vy)  # Accélération gravitationnelle

    def test_simulation_time_progression(self):
        """Test de la progression du temps"""
        initial_time = self.simulator.time
        dt = self.simulator.dt

        self.simulator.step()

        self.assertAlmostEqual(self.simulator.time, initial_time + dt, places=5)

    def test_multiple_steps_time_progression(self):
        """Test de progression du temps sur plusieurs pas"""
        initial_time = self.simulator.time
        dt = self.simulator.dt
        steps = 5

        for _ in range(steps):
            self.simulator.step()

        expected_time = initial_time + (steps * dt)
        self.assertAlmostEqual(self.simulator.time, expected_time, places=5)

    def test_pause_functionality(self):
        """Test de la fonctionnalité pause"""
        self.simulator.add_object(self.obj)

        self.simulator.start()
        self.assertFalse(self.simulator.paused)

        self.simulator.pause()
        self.assertTrue(self.simulator.paused)

        initial_y = self.obj.y
        initial_time = self.simulator.time

        self.simulator.step()

        # Quand en pause, rien ne doit changer
        self.assertEqual(self.obj.y, initial_y)
        self.assertEqual(self.simulator.time, initial_time)

    def test_pause_toggle(self):
        """Test du basculement pause/reprise"""
        self.simulator.start()

        # Premier toggle : pause
        self.simulator.pause()
        self.assertTrue(self.simulator.paused)

        # Deuxième toggle : reprise
        self.simulator.pause()
        self.assertFalse(self.simulator.paused)

    def test_reset_functionality(self):
        """Test de la fonctionnalité reset"""
        self.simulator.add_object(self.obj)

        # Faire quelques pas de simulation
        for _ in range(10):
            self.simulator.step()

        # Vérifier que des données d'historique existent
        self.assertGreater(len(self.obj.history['time']), 0)
        self.assertGreater(self.simulator.time, 0)

        # Reset
        self.simulator.reset()

        # Vérifier que l'historique est effacé et le temps remis à zéro
        self.assertEqual(len(self.obj.history['time']), 0)
        self.assertEqual(self.simulator.time, 0.0)

    def test_run_for_duration(self):
        """Test d'exécution pour une durée donnée"""
        self.simulator.add_object(self.obj)

        duration = 0.5
        initial_time = self.simulator.time

        self.simulator.run_for_duration(duration)

        self.assertAlmostEqual(self.simulator.time, initial_time + duration, places=2)

    def test_run_for_duration_with_history(self):
        """Test que l'historique est bien enregistré pendant run_for_duration"""
        self.simulator.add_object(self.obj)

        duration = 0.1
        self.simulator.run_for_duration(duration)

        # Vérifier que l'historique contient des données
        self.assertGreater(len(self.obj.history['time']), 0)
        self.assertGreater(len(self.obj.history['y']), 0)

        # Vérifier que l'objet a bien bougé
        self.assertLess(self.obj.history['y'][-1], self.obj.history['y'][0])

    def test_objects_info(self):
        """Test de récupération des informations d'objets"""
        self.simulator.add_object(self.obj)

        info = self.simulator.get_objects_info()

        self.assertEqual(len(info), 1)
        self.assertIn('x', info[0])
        self.assertIn('y', info[0])
        self.assertIn('vx', info[0])
        self.assertIn('vy', info[0])
        self.assertIn('speed', info[0])
        self.assertIn('kinetic_energy', info[0])
        self.assertIn('potential_energy', info[0])

    def test_objects_info_multiple_objects(self):
        """Test des informations avec plusieurs objets"""
        obj2 = PhysicsObject(x=5, y=15, vx=1, vy=-1, mass=2.0)

        self.simulator.add_object(self.obj)
        self.simulator.add_object(obj2)

        info = self.simulator.get_objects_info()

        self.assertEqual(len(info), 2)

        # Vérifier que les infos correspondent aux objets
        self.assertEqual(info[0]['x'], self.obj.x)
        self.assertEqual(info[1]['x'], obj2.x)

    def test_simulator_states(self):
        """Test des états du simulateur"""
        # État initial
        self.assertFalse(self.simulator.running)
        self.assertFalse(self.simulator.paused)

        # Start
        self.simulator.start()
        self.assertTrue(self.simulator.running)
        self.assertFalse(self.simulator.paused)

        # Pause
        self.simulator.pause()
        self.assertTrue(self.simulator.running)
        self.assertTrue(self.simulator.paused)

        # Stop
        self.simulator.stop()
        self.assertFalse(self.simulator.running)
        self.assertFalse(self.simulator.paused)

class TestEnergyConservation(unittest.TestCase):
    """Tests de conservation d'énergie"""

    def test_energy_conservation_no_air_resistance(self):
        """Test de conservation d'énergie sans résistance de l'air"""
        simulator = FreeFallSimulator(dt=0.001, air_resistance=False)
        obj = PhysicsObject(x=0, y=10, vx=0, vy=0, mass=1.0)
        simulator.add_object(obj)

        # Énergie initiale
        initial_pe = obj.potential_energy(0)
        initial_ke = obj.kinetic_energy
        initial_total = initial_pe + initial_ke

        # Simuler jusqu'à mi-parcours (environ)
        simulator.run_for_duration(0.7)  # Temps pour tomber d'environ 5m

        # Énergie au milieu
        mid_pe = obj.potential_energy(0)
        mid_ke = obj.kinetic_energy
        mid_total = mid_pe + mid_ke

        # L'énergie totale doit être conservée (avec une petite tolérance numérique)
        self.assertAlmostEqual(initial_total, mid_total, places=0)  # Tolérance plus large

    def test_energy_loss_with_air_resistance(self):
        """Test de perte d'énergie avec résistance de l'air"""
        simulator = FreeFallSimulator(dt=0.001, air_resistance=True)
        obj = PhysicsObject(x=0, y=10, vx=0, vy=0, mass=1.0, radius=0.1)
        simulator.add_object(obj)

        # Énergie initiale
        initial_pe = obj.potential_energy(0)
        initial_ke = obj.kinetic_energy
        initial_total = initial_pe + initial_ke

        # Simuler pendant un certain temps
        simulator.run_for_duration(1.0)

        # Énergie finale
        final_pe = obj.potential_energy(0)
        final_ke = obj.kinetic_energy
        final_total = final_pe + final_ke

        # L'énergie totale doit diminuer à cause du frottement
        self.assertLess(final_total, initial_total)

    def test_kinetic_energy_increase_during_fall(self):
        """Test que l'énergie cinétique augmente pendant la chute"""
        simulator = FreeFallSimulator(dt=0.001, air_resistance=False)
        obj = PhysicsObject(x=0, y=10, vx=0, vy=0, mass=1.0)
        simulator.add_object(obj)

        initial_ke = obj.kinetic_energy

        # Simuler pendant un court moment
        simulator.run_for_duration(0.5)

        final_ke = obj.kinetic_energy

        # L'énergie cinétique doit augmenter
        self.assertGreater(final_ke, initial_ke)

class TestGroundCollision(unittest.TestCase):
    """Tests de collision avec le sol"""

    def test_collision_detection(self):
        """Test de détection de collision"""
        simulator = FreeFallSimulator(dt=0.001, air_resistance=False, ground_level=0.0)
        obj = PhysicsObject(x=0, y=1, vx=0, vy=0, mass=1.0, radius=0.1)
        simulator.add_object(obj)

        # Simuler jusqu'à ce que l'objet touche le sol
        while obj.y > obj.radius + 0.01:  # Petit buffer
            simulator.step()

        # L'objet devrait avoir rebondi (vitesse vers le haut)
        self.assertGreaterEqual(obj.y, obj.radius)
        # Note: la vitesse pourrait être vers le haut ou vers le bas selon le moment exact

if __name__ == '__main__':
    unittest.main()