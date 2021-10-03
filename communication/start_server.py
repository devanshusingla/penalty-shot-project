import gym

from server import PSServer

env = gym.make("gym_env:penalty-shot-v0")
server = PSServer(env)

server.start()