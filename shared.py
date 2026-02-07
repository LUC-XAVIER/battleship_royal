import random
import pickle
import struct
import time


class GameData:
    def __init__(self, data_type ="PLAYER_INFO"):
        self.type = data_type


class PlayerData(GameData):
    def __init__(self, name, addr="", color=""):
        super().__init__("PLAYER_INFO")
        self.name = name
        self.addr = addr
        self.color = color

    def __str__(self):
        return f"{self.type} {self.name} {self.addr} {self.color}"

    def __repr__(self):
        return self.__str__()

class Player:
    def __init__(self, sock, addr, name, color):
        self.sock = sock
        self.addr = addr
        self.name = name
        self.color = color

    def to_data(self):
        return PlayerData(self.name, self.addr, self.color)

class Room:
    def __init__(self):
        self.maxPlayers = 10
        self.playerHost = None
        self.players = []

def send(sock, data):
    # Serialize data
    data = pickle.dumps(data)

    # Pack the length of the serialised data
    header = struct.pack("!I", len(data))

    sock.sendall(header + data)

def _receive(sock, n):
    # Get exactly n bytes of data
    data = b''
    while len(data) < n:
        byt = sock.recv(n - len(data))
        if not byt:
            return None
        data += byt
    return data

def receive(sock):
    # Get a 4-byte header, the size of the data
    header = _receive(sock, 4)
    if header:
        # Deserialize the header
        length = struct.unpack('!I', header)[0]

        # Get actual message
        raw = _receive(sock, length)

        data = pickle.loads(raw)
        return data
    else:
        return None
