from utils.envs import MakeEnv
import torch

env = MakeEnv().create_env()
action_space = env.action_space["puck"]
action_shape = action_space.shape
state_space = env.observation_space
state_shape = state_space.shape

puck_params = {
    "sine": {},
    "greedy": {
        "agent": "puck",
        "disc_k": None,
    },
    "smurve": {},
    "ppo": {
        "init_params": {
            "state_shape": env.observation_space.shape,
            "action_space": action_space,
            "hidden_size": [128, 128],
        },
        "call_params": {
            "discount_factor": 1,
            "lr": 5e-4,
        },
    },
    "dqn": {"init_params": {}, "call_params": {}},
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
            "recurrent": True,
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
