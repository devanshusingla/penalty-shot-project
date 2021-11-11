import torch, numpy as np
from torch import nn
from datetime import datetime
import tianshou as ts
from tianshou.utils import TensorboardLogger, WandbLogger
from agents import TwoAgentPolicy
from agents.lib_agents import SinePolicy, GreedyPolicy
from agents.lib_agents import DQN
from utils import make_render_env, make_env, make_discrete_env, make_render_discrete_env
from functools import partial

# Hyper parameters for the example
NUM_TRAIN_ENVS = 3
NUM_TEST_ENVS = 5
BAR_ACTION_K = 7 # Number of action values to discretize into
env = make_discrete_env(BAR_ACTION_K)
BUFFER_SIZE = 2000
BUFFER_NUM = 10
PATH_TO_POLICY = "./opt_policy/policy_2021-11-11_09-06-08.pth"

# creating policies
p1 = SinePolicy()
# p2 = GreedyPolicy(agent='bar', disc_k=7)
p2 = DQN(
    env.observation_space.shape, 
    env.action_space['bar'].shape
    )(
        discount_factor=0.99, 
        estimation_step=5, 
        target_update_freq=320
    )
policy = TwoAgentPolicy(observation_space=env.observation_space, action_space=env.action_space, policies=(p1, p2))
policy.load_state_dict(torch.load(PATH_TO_POLICY))
policy.eval()

test_envs = ts.env.DummyVectorEnv([partial(make_render_discrete_env, k=BAR_ACTION_K, eps=1) for _ in range(1)])
test_collector = ts.data.Collector(
    policy, 
    test_envs, exploration_noise=True)

result = test_collector.collect(n_episode=100)
print(result)

