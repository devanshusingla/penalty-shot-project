import socket, pickle, json
from _thread import *
from importlib.resources import open_text

with open_text("communication", "config.json") as f:
    config = json.load(f)
    host = config["host"]
    port = config["port"]
    msg_length = config["msg length"]


class PSClient:
    def __init__(self, id):
        self.id = id

        self.sock = socket.socket()
        print("created socket successfully")

    def connect(self, host=host, port=port):
        self.sock.connect((host, port))
        self.sock.send(str.encode(self.id))

        msg = self.sock.recv(msg_length)
        if msg.decode() != "connected":
            print("disconnected")
            return None

        self.sock.send(str.encode("start"))

        msg = self.sock.recv(msg_length)
        if not msg:
            print("disconnected")
            return None

        return pickle.loads(msg)

    def step(self, action):
        self.sock.send(pickle.dumps(action))

        msg = self.sock.recv(msg_length)
        if not msg:
            print("disconnected")
            return None
        res = pickle.loads(msg)

        return res

    def close(self):
        self.sock.close()
