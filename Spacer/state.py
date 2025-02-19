import random

class GameState:
    def __init__(self):
        self.camera_pos = [0.0, 0.0, 0.0]
        self.camera_rot = 0.0
        self.camera_tilt = 0.0
        self.zoom = -10.0
        self.stations = self.generate_stations()
        self.selected_station = None
        self.moving_to_station = False
        self.move_timer = 0

    def generate_stations(self, num_stations=12):
        stations = []
        for _ in range(num_stations):
            x = random.uniform(-35, 35)
            y = random.uniform(-15, 15)
            z = random.uniform(-35, 35)
            stations.append({
                'pos': [x, y, z],
                'color': (random.random(), random.random(), random.random())
            })
        return stations

    def reset_camera(self):
        self.camera_pos = [0.0, 0.0, 0.0]
        self.camera_rot = 0.0
        self.camera_tilt = 0.0

    def update(self):
        if self.move_timer > 0:
            self.move_timer = max(0, self.move_timer - 1/60)