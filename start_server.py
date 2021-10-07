import gym

from communication import PSServer

env = gym.make("gym_env:penalty-shot-v0")
server = PSServer(env, save_run=True, save_path= "./sample_runs/move_sine vs hardcoded_baseline_adaptive.gif")

server.start()