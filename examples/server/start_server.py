import gym

from communication import PSServer

env = gym.make("gym_env:penalty-shot-v0")
server = PSServer(
    env,
)

server.start()
