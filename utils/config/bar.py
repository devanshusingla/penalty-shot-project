from utils.envs import MakeEnv
import torch
from tianshou.exploration import GaussianNoise

env = MakeEnv().create_env()
action_space = env.action_space["bar"]
action_shape = action_space.shape
state_space = env.observation_space
state_shape = state_space.shape

bar_params = {
    "greedy": {"agent": "bar", "disc_k": None},
    "sine": {},
    "ppo": {
        "init_params": {
            "state_shape": env.observation_space.shape,
            "action_space": action_space,
            "hidden_size": [128, 128],
        },
        "call_params": {"discount_factor": 0.99},
    },
    "dqn": {
        "init_params": {
            "state_shape": state_shape,
            "action_shape": action_shape,
            "device": "cuda",
            "lr": 0.001,
        },
        "call_params": {},
    },
    "sac": {
        "init_params": {
            "action_space": action_space,
            "state_shape": state_shape,
            "action_shape": action_shape,
            "action_hidden_shape": [128, 128],
            "critic_hidden_shape": [128, 128],
            "device": "cuda" if torch.cuda.is_available() else "cpu",
        },
        "call_params": {
            "actor_lr": 0.001,
            "critic_lr": 0.001,
            "tau": 0.005,
            "gamma": 1.0,
            "n_step": 4,
            "recurrent": False,
            "exploration_noise": GaussianNoise(sigma=0.3)
        },
    },
    "ddpg": {
        "init_params": {
            "action_space": action_space,
            "state_shape": state_shape,
            "action_shape": action_shape,
            "action_hidden_shape": [128, 128],
            "critic_hidden_shape": [128, 128],
            "device": "cuda" if torch.cuda.is_available() else "cpu",
        },
        "call_params": {
            "actor_lr": 0.001,
            "critic_lr": 0.001,
            "tau": 0.005,
            "gamma": 1.0,
            "n_step": 4,
        },
    },
    "td3": {
        "init_params": {
            "action_space": action_space,
            "state_shape": state_shape,
            "action_shape": action_shape,
            "action_hidden_shape": [128, 128],
            "critic_hidden_shape": [128, 128],
            "device": "cuda" if torch.cuda.is_available() else "cpu",
        },
        "call_params": {
            "actor_lr": 0.001,
            "critic_lr": 0.001,
            "tau": 0.005,
            "gamma": 1.0,
            "n_step": 4,
        },
    },
}
