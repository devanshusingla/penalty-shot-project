import torch, numpy as np
from torch import nn

import tianshou as ts
from tianshou.utils import TensorboardLogger, WandbLogger

from agents import TwoAgentPolicy
from agents.lib_agents import SinePolicy
from agents.lib_agents import DQN

from utils import make_render_env, make_env, make_discrete_env, make_render_discrete_env

# create environment

env = make_discrete_env()
train_envs = ts.env.DummyVectorEnv([make_discrete_env for _ in range(3)])
test_envs = ts.env.DummyVectorEnv([make_render_discrete_env for _ in range(5)])

# creating policies

policy_puck = SinePolicy()
policy_bar = DQN(env.observation_space.shape, env.action_space["bar"].shape)(
    discount_factor=0.9, estimation_step=3, target_update_freq=320
)
policy = TwoAgentPolicy(
    observation_space=env.observation_space,
    action_space=env.action_space,
    policies=(policy_puck, policy_bar),
)

# setup collector

train_collector = ts.data.Collector(
    policy, train_envs, ts.data.VectorReplayBuffer(2000, 10), exploration_noise=True
)
test_collector = ts.data.Collector(policy, test_envs, exploration_noise=True)

# logging
# First sign in on wandb

logger = WandbLogger(
    save_interval=1,
    project="Penalty-Shot-Game",
    name="Devanshu Singla",
    entity="dsingla",
    run_id="your-api-key-available-on-website",
)

# training

result = ts.trainer.offpolicy_trainer(
    policy,
    train_collector,
    test_collector,
    max_epoch=10,
    step_per_epoch=10000,
    step_per_collect=10,
    update_per_step=0.1,
    episode_per_test=100,
    batch_size=64,
)  # , logger=logger)
print(f"Finished training! Use {result}")
