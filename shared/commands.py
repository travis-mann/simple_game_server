from enum import Enum

class Commands(Enum):
    ACK = bytes(0)
    UP = bytes(1)
    DOWN = bytes(2)
    LEFT = bytes(3)
    RIGHT = bytes(4)
    FIRE = bytes(5)
    