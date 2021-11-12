
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
from utils import general_make_env



# Hyper parameters for the example
NUM_TRAIN_ENVS = 3
NUM_TEST_ENVS = 5
BAR_ACTION_K = 7 # Number of action values to discretize into
BUFFER_SIZE = 2000
BUFFER_NUM = 10

# Parameters for environment
train_params = {
    'flatten' : {},
    # 'discrete': {
    #     'k': BAR_ACTION_K,
    # }
}
test_params = {
    'flatten' : {},
    'render': {
        'eps': 0.02
    },
    # 'discrete': {
    #     'k': BAR_ACTION_K,
    # }
}
env = general_make_env(params=train_params)
# creating policies
p1 = SinePolicy()
# p2 = GreedyPolicy(agent='bar', disc_k=7)
# p2 = DQN(
#     env.observation_space.shape, 
#     env.action_space['bar'].shape
#     )(
#         discount_factor=0.99, 
#         estimation_step=5, 
#         target_update_freq=320
#     )
p2 = PPO(
    env.observation_space.shape,
    env.action_space['bar']
    )(
        discount_factor=0.99,
    )

policy = TwoAgentPolicy(observation_space=env.observation_space, action_space=env.action_space, policies=(p1, p2))


# create environment
train_envs = ts.env.DummyVectorEnv([partial(general_make_env, params=train_params) for _ in range(NUM_TRAIN_ENVS)])
test_envs = ts.env.DummyVectorEnv([partial(general_make_env, params=test_params) for _ in range(NUM_TEST_ENVS)])

# setup collector
train_collector = ts.data.Collector(
    policy, 
    train_envs, 
    ts.data.VectorReplayBuffer(BUFFER_SIZE, BUFFER_NUM), exploration_noise=True)
test_collector = ts.data.Collector(
    policy, 
    test_envs, exploration_noise=True)


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
    policy, train_collector, test_collector,
    max_epoch=10, 
    step_per_epoch=10000, 
    repeat_per_collect=2,
    episode_per_test=100, 
    batch_size=64,
    # update_per_step=0.1, 
    episode_per_collect=10,    
    
    #  logger=logger
     )
np.stack()
print(f'Finished training! Use {result}')

torch.save(policy.state_dict(), './opt_policy/policy_{:%Y-%m-%d_%H-%M-%S}.pth'.format(datetime.now()))