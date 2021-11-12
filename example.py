import torch, numpy as np
from torch import nn

import tianshou as ts
from tianshou.utils import TensorboardLogger, WandbLogger
from torch.utils.tensorboard import SummaryWriter, writer

from agents import TwoAgentPolicy
from agents.lib_agents import SinePolicy
from agents.lib_agents import SAC

from utils import make_render_env, make_env, make_discrete_env, make_render_discrete_env

env = make_env()
train_envs = ts.env.DummyVectorEnv([make_env for _ in range(10)])
test_envs = ts.env.DummyVectorEnv([make_render_env for _ in range(5)])

# creating policies

p1 = SinePolicy()
p2 = SAC(
    env.action_space["bar"], env.observation_space.shape, env.action_space["bar"].shape
)(n_step=1)
policy = TwoAgentPolicy(
    observation_space=env.observation_space,
    action_space=env.action_space,
    policies=(p1, p2),
)

# setup collector

train_collector = ts.data.Collector(
    policy,
    train_envs,
    ts.data.VectorReplayBuffer(2000, len(train_envs)),
    exploration_noise=True,
)
test_collector = ts.data.Collector(policy, test_envs, exploration_noise=True)

# logging
logger = WandbLogger(
    save_interval=1,
    project="test-project",
    name="Devanshu Singla",
    entity="penalty-shot-project",
    run_id="sac",
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
    batch_size=4,
)  # , logger=logger)
print(f"Finished training! Use {result}")
