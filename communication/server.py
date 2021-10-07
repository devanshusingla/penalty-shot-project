import socket, pickle, json, time
from queue import Queue
from _thread import *
from threading import Event
from importlib.resources import open_text

with open_text('communication','config.json') as f:
    config = json.load(f)
    host = config['host']
    port = config['port']
    msg_length = config['msg length']
    initial_time_lapse = config['initial time lapse']
    frame_time_lapse = config['frame time lapse']
    final_time_lapse = config['final time lapse']

class PSServer:
    def __init__(self, env, port=port):
        self.env = env
        self.port = port
        self.bar = None
        self.puck = None

        self.agents_ready = Event()
    
    def start(self):
        start_new_thread(self.run_server, ())

        while True:
            self.agents_ready.wait()
            self.play()
            self.agents_ready.clear()
    
    def run_server(self):
        server_sock = socket.socket()
        print("server socket created successfully")

        server_sock.bind(('', self.port))
        print("socket binded to port {}".format(server_sock.getsockname()[1]))

        server_sock.listen(2)
        print("socket is listening")

        while True:
            sock, addr = server_sock.accept()
            print("got connection from {}".format(addr))

            start_new_thread(self.add_agent, (sock, ))
    
    def add_agent(self, agent):
        agent_id = agent.recv(msg_length)
        if not agent_id:
            print("{} closed connection".format(agent.getsockname()[1]))

        print("{} requested to play as {}".format(agent.getsockname()[1], agent_id.decode()))
        if agent_id.decode() == 'P':
            if self.puck is not None:
                print("puck is already assigned closing connection")
                agent.close()
            else:
                self.puck = agent
                agent.send(str.encode("connected"))
                print("{} playing as puck".format(agent.getsockname()[1]))

        elif agent_id.decode() == 'B':
            if self.bar is not None:
                print("bar is already assigned closing connection")
                agent.close()
            else:
                self.bar = agent
                agent.send(str.encode("connected"))
                print("{} playing as bar".format(agent.getsockname()[1]))
        
        if self.puck is not None and self.bar is not None:
            self.agents_ready.set()

    def play(self):
        msg_puck = self.puck.recv(msg_length)
        msg_bar = self.bar.recv(msg_length)

        if msg_puck.decode() != 'start' or msg_bar.decode() != 'start':
            print("agents not starting game")
            return

        print("starting the game")

        state, done = self.env.reset()

        self.puck.send(pickle.dumps((state, done)))
        self.bar.send(pickle.dumps((state, done)))
        
        time.sleep(initial_time_lapse)

        self.env.render()
        time.sleep(frame_time_lapse)
        while not done:
            msg = self.puck.recv(msg_length)
            if not msg:
                print("agent puck disconnected")
                break
            puck_action = pickle.loads(msg)

            msg = self.bar.recv(msg_length)
            if not msg:
                print("agent bar disconnected")
                break
            bar_action = pickle.loads(msg)

            res = self.env.step(puck_action, bar_action)
            self.puck.send(pickle.dumps(res))
            self.bar.send(pickle.dumps(res))

            self.env.render()
            time.sleep(frame_time_lapse)

            done = res[2]

        print("quitting game")

        time.sleep(final_time_lapse)

        self.env.close()
        self.puck.close()
        self.bar.close()
        self.puck = None
        self.bar = None