class GameState:
    def __init__(self):
        self.server_data = None
        self.player_id = 0
        self.map = ""
        self.map_height = 0

    def load_map(self, map: str):
        self.map = map
        self.map_height = map.count("\n") + 1
