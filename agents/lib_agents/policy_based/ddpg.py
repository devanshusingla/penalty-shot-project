from tianshou.policy import DDPGPolicy
from tianshou.utils.net.common import Net
from tianshou.utils.net.continuous import Actor, ActorProb, Critic
from tianshou.exploration import GaussianNoise

import torch, numpy as np
from torch import nn
from torch._C import device

class DDPG:
    def __init__(self, action_space, state_shape, action_shape, actor_hidden_shape = [128, 128], critic_hidden_shape = [128, 128], **kwargs):
        self.action_space = action_space
        self.state_shape = state_shape
        self.action_shape = action_shape
        self.actor_hidden_shape = actor_hidden_shape
        self.critic_hidden_shape = critic_hidden_shape
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.noise = GaussianNoise(sigma=0.3)

    def __call__(self, actor_lr = 0.001, critic_lr = 0.001, tau=0.005, gamma=1.0, n_step=4, **kwargs):
        actor_net = Net(self.state_shape, hidden_sizes=self.actor_hidden_shape, device=self.device)
        actor = Actor(actor_net, self.action_shape, self.actor_hidden_shape, max_action= 1, device=self.device).to(self.device)
        actor_opt = torch.optim.Adam(actor.parameters(), lr=actor_lr)

        critic_net = Net(self.state_shape, self.action_shape, hidden_sizes=self.critic_hidden_shape, concat=True, device=self.device)
        critic = Critic(critic_net, device=self.device).to(self.device)
        critic_opt = torch.optim.Adam(critic.parameters(), lr=critic_lr)

        return DDPGPolicy(
            actor,
            actor_opt,
            critic,
            critic_opt,
            tau = tau,
            gamma=gamma,
            estimation_step = n_step,
            exploration_noise=self.noise,
            action_space = self.action_space
        )