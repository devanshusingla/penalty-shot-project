from torch import optim
from tianshou.policy import PPOPolicy
import torch, numpy as np
from torch import nn
from tianshou.policy.base import BasePolicy
from tianshou.utils.net.common import Net

class PPO:
    def __init__(self, state_shape, action_shape, **kwargs):
        super().__init__()
        self.actor = Net(state_shape, action_shape, hidden_sizes=[128, 128])
        self.critic = Net(state_shape, [1], hidden_sizes=[128, 128])
        self.optim = torch.optim.Adam(list(self.actor.parameters()) + list(self.critic.parameters()), lr=1e-3)


    def __call__(self, **kwargs):
        return PPOPolicy(
            actor=self.actor,
            critic=self.critic,
            dist_fn=torch.distributions.OneHotCategorical,
            optim=self.optim,
            **kwargs)
    
    def __name__(self):
        return "PPO"