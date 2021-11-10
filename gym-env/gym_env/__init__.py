"""In this file we register the environments created with gym. This is useful if we want to to later use gym directly
to run baseline algorithms provided by it.
"""
from gym.envs.registration import register

register(id="penalty-shot-v0", entry_point="gym_env.envs:PSE")
