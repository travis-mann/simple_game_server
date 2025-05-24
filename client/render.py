# --- imports ---
from client.game_state import GameState
from time import time


# --- private ---
def _clear_lines(n: int):
    for _ in range(n):
        print("\033[F\033[K", end='')  # \033[F = move cursor up, \033[K = clear line


# --- public ---
def draw_game_object(game_object: dict, icon: str, lines: list) -> None:
    try:
        pos = game_object["POSITION"]
        line_chars = list(lines[pos[1]])
        line_chars[pos[0]] = icon
        lines[pos[1]] = "".join(line_chars)
    except IndexError:
        pass


def render(game_state: GameState) -> None:
    if game_state.server_data is None:
        return
    
    _clear_lines(game_state.map_height + 2)
    lines = game_state.map.split("\n")
    players = game_state.server_data["PLAYERS"].values()
    for player in players:
        draw_game_object(player, "O", lines)
    for missile in game_state.server_data["MISSILES"]:
        draw_game_object(missile, ".", lines)

    print(f"Health: {game_state.server_data['PLAYERS'][game_state.player_id]['HEALTH']}")
    print(f"Players: {game_state.server_data['PLAYERS']}")
    for line in lines:
        print(line)
