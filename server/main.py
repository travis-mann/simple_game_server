# --- imports ---
import json
import random
import socket
from typing import Tuple
from shared.commands import Commands
from shared.directions import Directions


# --- globals ---
GAME_STATE = {"PLAYERS": {}, "MISSILES": []}
ADDR_ID_MAP = {}
with open(r"maps\map_1.txt") as f:
    MAP_LINES = f.readlines()

# --- func ---
def get_server_socket(port: int) -> None:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(("0.0.0.0", port))
    server_socket.settimeout(3)
    return server_socket


def get_new_client_id() -> int:
    id = random.randint(0, 1000)
    while id in ADDR_ID_MAP.values():
        id = random.randint(0, 1000)
    return id


def connect_client(addr: Tuple[str, int], clients: set) -> int:
    if addr not in clients:
        clients.add(addr)
    id = get_new_client_id()
    ADDR_ID_MAP[addr] = id
    GAME_STATE["PLAYERS"][id] = {"POSITION": (1,1), "HEALTH": 5, "DIRECTION": Directions.RIGHT.value}
    server_socket.sendto(str(id).encode(), addr)
    return id


def remove_client(clients: set, client: tuple) -> None:
    clients.remove(client)
    id = ADDR_ID_MAP[client]
    del ADDR_ID_MAP[client]
    del GAME_STATE["PLAYERS"][id]
    print(f"{client} disconnected")


def disconnect_non_responsive_clients(server_socket: socket.socket, clients: set) -> None:
    clients_to_remove = []
    for client in clients.copy():
        try:
            server_socket.sendto(Commands.ACK.value, client)
            server_socket.recvfrom(1024)
        except (socket.timeout, ConnectionResetError):
            clients_to_remove.append(client)
    for client in clients_to_remove:
        remove_client(clients, client)

def broadcast_updates(server_socket: socket.socket, clients: set) -> None:
    json_bytes = json.dumps(GAME_STATE).encode('utf-8')
    for client in clients:
        server_socket.sendto(json_bytes, client)


def is_wall(pos: tuple) -> bool:
    return MAP_LINES[pos[1]][pos[0]] in ["|", "-"]


def update_position(game_object: dict, direction: int, amount: int = 1) -> bool:
    current_pos = game_object["POSITION"]
    if direction == Directions.LEFT.value:
        new_pos = (current_pos[0] - amount, current_pos[1])
    elif direction == Directions.RIGHT.value:
        new_pos = (current_pos[0] + amount, current_pos[1])
    elif direction == Directions.UP.value:
        new_pos = (current_pos[0], current_pos[1] - amount)
    elif direction == Directions.DOWN.value:
        new_pos = (current_pos[0], current_pos[1] + amount)
    
    pos_updated = False
    if not is_wall(new_pos):
        game_object["POSITION"] = new_pos
        pos_updated = True
    if direction is not None:
        game_object["DIRECTION"] = direction
    return pos_updated


def get_player_id(addr, clients):
    if addr in ADDR_ID_MAP:
        return ADDR_ID_MAP[addr]
    return connect_client(addr, clients)


def fire_missile(player_id: int) -> None:
    player_pos = GAME_STATE["PLAYERS"][player_id]["POSITION"]
    direction = GAME_STATE["PLAYERS"][player_id]["DIRECTION"]
    GAME_STATE["MISSILES"].append({"POSITION": player_pos, "DIRECTION": direction})


def check_collision(missile: dict) -> None:
    for player_id, player in GAME_STATE["PLAYERS"].items():
        if player["POSITION"] == missile["POSITION"]:
            print(f"{player_id} hit!")
            player["HEALTH"] -= 1


def update_missiles() -> None:
    missiles_to_remove = []
    for missile in GAME_STATE["MISSILES"]:
        if not update_position(missile, missile["DIRECTION"]):
            missiles_to_remove.append(missile)
        else:
            check_collision(missile)
    for missile in missiles_to_remove:
        GAME_STATE["MISSILES"].remove(missile)


def server_iteration(server_socket: socket.socket, clients: set) -> None:
    try:
        data, addr = server_socket.recvfrom(1024)
        player_id = get_player_id(addr, clients)
        if data == Commands.LEFT.value:
            update_position(GAME_STATE["PLAYERS"][player_id], Directions.LEFT.value)
        elif data == Commands.RIGHT.value:
            update_position(GAME_STATE["PLAYERS"][player_id], Directions.RIGHT.value)
        elif data == Commands.UP.value:
            update_position(GAME_STATE["PLAYERS"][player_id], Directions.UP.value)
        elif data == Commands.DOWN.value:
            update_position(GAME_STATE["PLAYERS"][player_id], Directions.DOWN.value)
        elif data == Commands.FIRE.value:
            fire_missile(player_id)
        update_missiles()
        broadcast_updates(server_socket, clients)
    except ConnectionResetError:
        disconnect_non_responsive_clients(server_socket, clients)
    except socket.timeout:
        pass


def server_loop(server_socket: socket.socket) -> None:
    print("starting server loop")
    clients = set()
    while True:
        try:
            server_iteration(server_socket, clients)
        except KeyboardInterrupt:
            print("keyboard interrupt detected")
            break
    server_socket.close()
    print("server socket closed")


if __name__ == "__main__":
    server_socket = get_server_socket(9999)
    server_loop(server_socket)
