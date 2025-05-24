# --- imports ---
import json
from time import sleep
import socket
import keyboard
import threading
from typing import Tuple
from shared.commands import Commands
from client.render import render
from client.game_state import GameState
from client.server_connect import connect

# --- globals ---
GAME_STATE = GameState()
with open(r"maps\map_1.txt") as f:
    GAME_STATE.load_map(f.read())
EXIT = threading.Event()


# --- func ----
def listen_to_server(client_socket: socket.socket, server_address: Tuple[str, int]) -> None:
    while not EXIT.is_set():
        try:
            data, _ = client_socket.recvfrom(1024)
        except socket.timeout:
            continue
        if data == Commands.ACK.value:
            client_socket.sendto(Commands.ACK.value, server_address)
            continue 
        try:
            GAME_STATE.server_data = json.loads(data.decode())
        except json.decoder.JSONDecodeError:
            pass


def listen_to_keyboard(client_socket: socket.socket, server_address: Tuple[str, int]) -> None:
    global EXIT
    while not EXIT.is_set():
        if keyboard.is_pressed('esc'):
            print("disconnecting...")
            EXIT.set()
        if keyboard.is_pressed('w'):
            client_socket.sendto(Commands.UP.value, server_address)
        elif keyboard.is_pressed('s'):
            client_socket.sendto(Commands.DOWN.value, server_address)
        if keyboard.is_pressed('a'):
            client_socket.sendto(Commands.LEFT.value, server_address)
        elif keyboard.is_pressed('d'):
            client_socket.sendto(Commands.RIGHT.value, server_address)
        if keyboard.is_pressed('space'):
            client_socket.sendto(Commands.FIRE.value, server_address)
        sleep(0.1)


def game_loop(client_socket: socket.socket, server_address: Tuple[str, int]) -> None:
    global EXIT
    print("running game loop")
    server_listener_thread = threading.Thread(target=listen_to_server, args=(client_socket, server_address), daemon=True)
    server_listener_thread.start()
    keyboard_listener_thread = threading.Thread(target=listen_to_keyboard, args=(client_socket, server_address), daemon=True)
    keyboard_listener_thread.start()
    while not EXIT.is_set():
        try:
            render(GAME_STATE)
            if GAME_STATE.server_data['PLAYERS'][GAME_STATE.player_id]['HEALTH'] <= 0:
                print("GAME OVER, disconnecting...")
                EXIT.set()
            sleep(0.1)
        except KeyboardInterrupt:
            print("keyboard interrupt detected, disconnecting...")
            EXIT.set()
    server_listener_thread.join()
    keyboard_listener_thread.join()
    client_socket.close()


if __name__ == "__main__":
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address, GAME_STATE.player_id = connect(client_socket)
    game_loop(client_socket, server_address)
