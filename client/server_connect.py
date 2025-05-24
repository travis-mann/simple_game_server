# --- imports ---
import socket
from typing import Tuple
from shared.commands import Commands


# --- private ---
def _get_server_address() -> Tuple[str, int]:
    while True:
        ip_and_port = input("server address (<ip>:<port>): ")
        if ip_and_port.count(":") != 1:
            print('ERROR: Address must be provided as "<ip>:<port>"')
            continue
        ip, port = ip_and_port.split(":")
        return (ip, int(port)) 


# --- public ---
def connect(client_socket: socket.socket) -> Tuple[Tuple[str, int], int]:
    while True:
        server_address = ("localhost", 9999)  # _get_server_address()
        try:
            client_socket.sendto(Commands.ACK.value, server_address)
            client_socket.settimeout(5)
            data, ret_addr = client_socket.recvfrom(1024)
            player_id = data.decode()
            print(f"player id is: {player_id}")
            return (ret_addr, player_id)
        except Exception as e:
            print(f"ERROR ({type(e)}): Failed to connect to {server_address}, try again.")
