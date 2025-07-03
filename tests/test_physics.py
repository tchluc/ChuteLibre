"""Tests unitaires pour le moteur physique"""

import unittest
import sys
import os
import math

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.models.physics_object import PhysicsObject
from src.models.physics_engine import PhysicsEngine
from src.simulation.numerical_methods import EulerMethod
from src.utils.constants import GRAVITY

class TestPhysicsObject(unittest.TestCase):
    """Tests pour la classe PhysicsObject"""

    def setUp(self):
        """Initialisation avant chaque test"""
        self.obj = PhysicsObject(x=0, y=10, vx=0, vy=0, mass=1.0, radius=0.1)

    def test_initialization(self):
        """Test de l'initialisation"""
        self.assertEqual(self.obj.x, 0)
        self.assertEqual(self.obj.y, 10)
        self.assertEqual(self.obj.mass, 1.0)
        self.assertEqual(self.obj.radius, 0.1)

    def test_area_calculation(self):
        """Test du calcul de l'aire"""
        expected_area = math.pi * (0.1 ** 2)
        self.assertAlmostEqual(self.obj.area, expected_area, places=5)

    def test_speed_calculation(self):
        """Test du calcul de la vitesse"""
        self.obj.vx = 3.0
        self.obj.vy = 4.0
        self.assertAlmostEqual(self.obj.speed, 5.0, places=5)

    def test_kinetic_energy(self):
        """Test du calcul de l'énergie cinétique"""
        self.obj.vx = 2.0
        self.obj.vy = 0.0
        expected_ke = 0.5 * 1.0 * 4.0  # 0.5 * m * v²
        self.assertAlmostEqual(self.obj.kinetic_energy, expected_ke, places=5)

    def test_potential_energy(self):
        """Test du calcul de l'énergie potentielle"""
        expected_pe = 1.0 * GRAVITY * 10.0  # m * g * h
        self.assertAlmostEqual(self.obj.potential_energy(0), expected_pe, places=5)

class TestPhysicsEngine(unittest.TestCase):
    """Tests pour le moteur physique"""

    def setUp(self):
        """Initialisation avant chaque test"""
        self.engine = PhysicsEngine(air_resistance=False)
        self.obj = PhysicsObject(x=0, y=10, vx=0, vy=0, mass=1.0)

    def test_gravity_force_only(self):
        """Test de la force gravitationnelle seule"""
        force_x, force_y = self.engine.calculate_forces(self.obj)
        self.assertEqual(force_x, 0.0)
        self.assertAlmostEqual(force_y, -GRAVITY, places=5)

    def test_air_resistance_force(self):
        """Test de la force de résistance de l'air"""
        self.engine.air_resistance = True
        self.obj.vy = -10.0  # Vitesse vers le bas

        force_x, force_y = self.engine.calculate_forces(self.obj)

        # La force de frottement doit s'opposer au mouvement
        self.assertEqual(force_x, 0.0)
        # Avec le frottement, la force totale vers le bas doit être réduite
        # (force_y sera moins négative que -GRAVITY car le frottement s'oppose)
        self.assertGreater(force_y, -GRAVITY)  # Corrigé: Greater au lieu de Less
        self.assertLess(force_y, 0)  # Mais toujours vers le bas

    def test_air_resistance_upward_motion(self):
        """Test de la résistance de l'air lors d'un mouvement vers le haut"""
        self.engine.air_resistance = True
        self.obj.vy = 10.0  # Vitesse vers le haut

        force_x, force_y = self.engine.calculate_forces(self.obj)

        # Avec mouvement vers le haut, le frottement s'ajoute à la gravité
        self.assertEqual(force_x, 0.0)
        self.assertLess(force_y, -GRAVITY)  # Plus négatif que la gravité seule

    def test_no_air_resistance_at_zero_speed(self):
        """Test qu'il n'y a pas de frottement à vitesse nulle"""
        self.engine.air_resistance = True
        self.obj.vx = 0.0
        self.obj.vy = 0.0

        force_x, force_y = self.engine.calculate_forces(self.obj)

        # Pas de frottement à vitesse nulle
        self.assertEqual(force_x, 0.0)
        self.assertAlmostEqual(force_y, -GRAVITY, places=5)

    def test_horizontal_air_resistance(self):
        """Test de la résistance de l'air horizontale"""
        self.engine.air_resistance = True
        self.obj.vx = 5.0  # Vitesse horizontale vers la droite
        self.obj.vy = 0.0  # Pas de vitesse verticale

        force_x, force_y = self.engine.calculate_forces(self.obj)

        # Force de frottement horizontale s'oppose au mouvement
        self.assertLess(force_x, 0)  # Force vers la gauche (oppose vx > 0)

        # Force verticale = gravité + composante verticale du frottement
        # Comme vy = 0, la composante verticale du frottement est 0
        # Donc force_y devrait être proche de -GRAVITY
        self.assertAlmostEqual(force_y, -GRAVITY, places=3)

    def test_ground_collision(self):
        """Test de la collision avec le sol"""
        self.obj.y = -0.05  # Sous le sol
        self.obj.vy = -5.0   # Vitesse vers le bas
        self.obj.radius = 0.1

        collision = self.engine.handle_ground_collision(self.obj)

        self.assertTrue(collision)
        self.assertGreaterEqual(self.obj.y, self.obj.radius)  # Au-dessus du sol
        self.assertGreater(self.obj.vy, 0)  # Vitesse inversée

    def test_no_collision_above_ground(self):
        """Test qu'il n'y a pas de collision au-dessus du sol"""
        self.obj.y = 5.0  # Bien au-dessus du sol
        self.obj.vy = -2.0

        collision = self.engine.handle_ground_collision(self.obj)

        self.assertFalse(collision)
        self.assertEqual(self.obj.y, 5.0)  # Position inchangée
        self.assertEqual(self.obj.vy, -2.0)  # Vitesse inchangée

    def test_derivatives_calculation(self):
        """Test du calcul des dérivées"""
        derivatives = self.engine.calculate_derivatives(0, 10, 5, -2, self.obj)

        # dx/dt = vx, dy/dt = vy
        self.assertEqual(derivatives[0], 5)  # dx/dt
        self.assertEqual(derivatives[1], -2)  # dy/dt
        self.assertEqual(derivatives[2], 0)   # dvx/dt (pas de force horizontale)
        self.assertAlmostEqual(derivatives[3], -GRAVITY, places=5)  # dvy/dt

class TestNumericalMethods(unittest.TestCase):
    """Tests pour les méthodes numériques"""

    def test_euler_method(self):
        """Test de la méthode d'Euler"""
        method = EulerMethod()

        def simple_derivatives(x, y, vx, vy):
            return vx, vy, 0, -GRAVITY

        initial_state = (0, 10, 0, 0)
        dt = 0.1

        new_state = method.step(initial_state, simple_derivatives, dt)

        # Après un pas d'Euler
        expected_x = 0 + 0 * dt  # x + vx * dt
        expected_y = 10 + 0 * dt  # y + vy * dt
        expected_vx = 0 + 0 * dt  # vx + ax * dt
        expected_vy = 0 + (-GRAVITY) * dt  # vy + ay * dt

        self.assertAlmostEqual(new_state[0], expected_x, places=5)
        self.assertAlmostEqual(new_state[1], expected_y, places=5)
        self.assertAlmostEqual(new_state[2], expected_vx, places=5)
        self.assertAlmostEqual(new_state[3], expected_vy, places=5)

    def test_euler_method_with_initial_velocity(self):
        """Test de la méthode d'Euler avec vitesse initiale"""
        method = EulerMethod()

        def simple_derivatives(x, y, vx, vy):
            return vx, vy, 0, -GRAVITY

        initial_state = (0, 10, 2, -1)  # Avec vitesses initiales
        dt = 0.1

        new_state = method.step(initial_state, simple_derivatives, dt)

        # Vérification des calculs
        expected_x = 0 + 2 * dt
        expected_y = 10 + (-1) * dt
        expected_vx = 2 + 0 * dt
        expected_vy = -1 + (-GRAVITY) * dt

        self.assertAlmostEqual(new_state[0], expected_x, places=5)
        self.assertAlmostEqual(new_state[1], expected_y, places=5)
        self.assertAlmostEqual(new_state[2], expected_vx, places=5)
        self.assertAlmostEqual(new_state[3], expected_vy, places=5)

class TestEdgeCases(unittest.TestCase):
    """Tests pour les cas limites"""

    def test_zero_mass_object(self):
        """Test avec un objet de masse nulle (doit lever une exception ou gérer gracieusement)"""
        try:
            obj = PhysicsObject(mass=0.0)
            engine = PhysicsEngine()
            # Cela pourrait causer une division par zéro
            derivatives = engine.calculate_derivatives(0, 10, 0, -1, obj)
            # Si on arrive ici, vérifier que l'accélération est infinie ou gérée
            self.assertTrue(abs(derivatives[3]) > 1000 or math.isinf(derivatives[3]))
        except ZeroDivisionError:
            # C'est acceptable aussi
            pass

    def test_very_high_speed(self):
        """Test avec une vitesse très élevée"""
        obj = PhysicsObject(vx=1000, vy=-1000, mass=1.0, radius=0.1)
        engine = PhysicsEngine(air_resistance=True)

        force_x, force_y = engine.calculate_forces(obj)

        # Les forces doivent être finies
        self.assertFalse(math.isinf(force_x))
        self.assertFalse(math.isinf(force_y))
        self.assertFalse(math.isnan(force_x))
        self.assertFalse(math.isnan(force_y))

if __name__ == '__main__':
    unittest.main()