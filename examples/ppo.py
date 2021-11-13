# from utils import train, get_args
# from utils.train import train

import torch, numpy as np
from torch import nn
from datetime import datetime
import tianshou as ts
from tianshou.policy.modelfree.ppo import PPOPolicy
from tianshou.utils import TensorboardLogger, WandbLogger
from agents import TwoAgentPolicy
from agents.lib_agents import SinePolicy, GreedyPolicy
from agents.lib_agents import DQN, PPO
from functools import partial
from utils import make_envs, MakeEnv


# Hyper parameters for the example
NUM_TRAIN_ENVS = 3
NUM_TEST_ENVS = 5
BAR_ACTION_K = 7  # Number of action values to discretize into
BUFFER_SIZE = 2000
BUFFER_NUM = 10

# Parameters for environment
train_params = {"modified_reward": "exp"}
test_params = {"modified_reward": "exp"}

env = MakeEnv().create_env()
# creating policies
p1 = SinePolicy()
p2 = PPO(env.observation_space.shape, env.action_space["bar"], hidden_sizes=[128, 128])(
    discount_factor=0.99,
)

policy = TwoAgentPolicy(
    observation_space=env.observation_space,
    action_space=env.action_space,
    policies=(p1, p2),
)


# create environment
train_envs = ts.env.DummyVectorEnv(make_envs(NUM_TRAIN_ENVS, **train_params)[1])
train_envs.seed(3)
test_envs = ts.env.DummyVectorEnv(make_envs(NUM_TEST_ENVS, **test_params)[1])
test_envs.seed(5)

# setup collector
train_collector = ts.data.Collector(
    policy,
    train_envs,
    ts.data.VectorReplayBuffer(BUFFER_SIZE, BUFFER_NUM),
    exploration_noise=True,
)
test_collector = ts.data.Collector(policy, test_envs, exploration_noise=True)


# logging
# First sign in on wandb
# logger = WandbLogger(
#     save_interval=1,
#     project="test-project",
#     name='Sarthak Rout',
#     entity='penalty-shot-project',
# )
# training

result = ts.trainer.onpolicy_trainer(
    policy,
    train_collector,
    test_collector,
    max_epoch=10,
    step_per_epoch=10000,
    repeat_per_collect=2,
    episode_per_test=100,
    batch_size=64,
    episode_per_collect=10,
    #  logger=logger
)
print(f"Finished training! Use {result}")

# torch.save(policy.state_dict(), './opt_policy/policy_{:%Y-%m-%d_%H-%M-%S}.pth'.format(datetime.now()))


#### DQN and Greedy Policy
# p2 = GreedyPolicy(agent='bar', disc_k=7)
# p2 = DQN(
#     env.observation_space.shape,
#     env.action_space['bar'].shape
#     )(
#         discount_factor=0.99,
#         estimation_step=5,
#         target_update_freq=320
#     )


# if __name__ == "__main__":
#     train(get_args())
