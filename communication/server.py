import socket, pickle, json, time
from queue import Queue
from _thread import *
from threading import Event
from importlib.resources import open_text
from matplotlib import animation
import matplotlib.pyplot as plt
import os

with open_text("communication", "config.json") as f:
    config = json.load(f)
    host = config["host"]
    port = config["port"]
    msg_length = config["msg length"]
    initial_time_lapse = config["initial time lapse"]
    frame_time_lapse = config["frame time lapse"]
    final_time_lapse = config["final time lapse"]


class PSServer:
    def __init__(self, env, port=port, save_run=False, save_path="./"):
        self.env = env
        self.port = port
        self.bar = None
        self.puck = None
        self.save_run = save_run
        self.save_path = save_path

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

        server_sock.bind(("", self.port))
        print("socket binded to port {}".format(server_sock.getsockname()[1]))

        server_sock.listen(2)
        print("socket is listening")

        while True:
            sock, addr = server_sock.accept()
            print("got connection from {}".format(addr))

            start_new_thread(self.add_agent, (sock,))

    def add_agent(self, agent):
        agent_id = agent.recv(msg_length)
        if not agent_id:
            print("{} closed connection".format(agent.getsockname()[1]))

        print(
            "{} requested to play as {}".format(
                agent.getsockname()[1], agent_id.decode()
            )
        )
        if agent_id.decode() == "P":
            if self.puck is not None:
                print("puck is already assigned closing connection")
                agent.close()
            else:
                self.puck = agent
                agent.send(str.encode("connected"))
                print("{} playing as puck".format(agent.getsockname()[1]))

        elif agent_id.decode() == "B":
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

        if msg_puck.decode() != "start" or msg_bar.decode() != "start":
            print("agents not starting game")
            return

        print("starting the game")

        done = False
        state = self.env.reset()

        self.puck.send(pickle.dumps((state, done)))
        self.bar.send(pickle.dumps((state, done)))

        time.sleep(initial_time_lapse)

        frames = []
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
            action = {"puck": puck_action, "bar": bar_action}
            res = self.env.step(action)
            self.puck.send(pickle.dumps(res))
            self.bar.send(pickle.dumps(res))

            if self.save_run:
                frames.append(self.env.render(mode="rgb_array"))
            else:
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
        if self.save_run:
            print("Saving run ...")
            self.save_render(frames)
        exit()

    def save_render(self, frames):
        plt.figure(
            figsize=(frames[0].shape[1] / 150.0, frames[0].shape[0] / 150.0), dpi=150
        )

        plt.axis("off")
        patch = plt.imshow(frames[0])

        def animate(i):
            patch.set_data(frames[i])

        anim = animation.FuncAnimation(
            plt.gcf(), animate, frames=len(frames), interval=60
        )
        writergif = animation.PillowWriter(fps=60)

        # check if folder exists
        index = self.save_path.rfind("/")
        folder_name = self.save_path[: index + 1]
        if not os.path.isdir(folder_name):
            print("Made folder {}".format(folder_name))
            os.mkdir(folder_name)

        anim.save(self.save_path, writer=writergif)
