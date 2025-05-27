from config import ball_types, ground_types, wind_speeds, heights

class SimulationData:
    """Classe pour gérer les données de la simulation"""
    def __init__(self):
        # Paramètres sélectionnés
        self.selected_ball = 0
        self.selected_ground = 0
        self.selected_wind = 0
        self.selected_height = 1

        # Valeurs calculées
        self.update_derived_values()

    def update_derived_values(self):
        """Met à jour les valeurs dérivées des sélections"""
        self.m = ball_types[self.selected_ball]["m"]
        self.k = ball_types[self.selected_ball]["k"]
        self.e = ground_types[self.selected_ground]["e"]
        self.wind_speed = wind_speeds[self.selected_wind]
        self.h0 = heights[self.selected_height]

    def get_selection_tuple(self):
        """Retourne un tuple des indices de sélection"""
        return (self.selected_ball, self.selected_ground, self.selected_wind, self.selected_height)

    def get_physics_parameters(self):
        """Retourne un dictionnaire des paramètres physiques"""
        return {
            'm': self.m,
            'k': self.k,
            'e': self.e,
            'wind_speed': self.wind_speed,
            'h0': self.h0,
            'selected_ball': self.selected_ball,
            'selected_ground': self.selected_ground
        }