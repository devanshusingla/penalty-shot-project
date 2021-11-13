from functools import partial
import torch, numpy as np
from torch import nn

import tianshou as ts
from tianshou.utils import TensorboardLogger, WandbLogger
from torch.cuda import is_available
from torch.utils.tensorboard import SummaryWriter, writer

from agents import TwoAgentPolicy
from agents.lib_agents import SinePolicy
from agents.lib_agents import SAC

from utils.envs import general_make_env

train_params = {"flatten": {}}
test_params = {"flatten": {}, "render": {"eps": 0.02}}
env = general_make_env(train_params)
train_envs = ts.env.DummyVectorEnv(
    [partial(general_make_env, params=train_params) for _ in range(10)]
)
test_envs = ts.env.DummyVectorEnv(
    [partial(general_make_env, test_params) for _ in range(5)]
)

# creating policies

p1 = SinePolicy()
p2 = SAC(
    env.action_space["bar"],
    env.observation_space.shape,
    env.action_space["bar"].shape,
    device="cuda" if torch.cuda.is_available() else "cpu",
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
    ts.data.VectorReplayBuffer(20, len(train_envs)),
    exploration_noise=True,
)
test_collector = ts.data.Collector(policy, test_envs, exploration_noise=True)

# logging
# logger = WandbLogger(
#     save_interval=1,
#     project="test-project",
#     name="Devanshu Singla",
#     entity="penalty-shot-project",
#     run_id="sac",
# )

# training
result = ts.trainer.offpolicy_trainer(
    policy,
    train_collector,
    test_collector,
    max_epoch=1,
    step_per_epoch=100,
    step_per_collect=10,
    update_per_step=0.1,
    episode_per_test=100,
    batch_size=4,
)  # , logger=logger)
print(f"Finished training! Use {result}")
