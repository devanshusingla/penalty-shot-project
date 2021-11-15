from tianshou.policy import TD3Policy
from tianshou.utils.net.common import Net
from tianshou.utils.net.continuous import (
    Actor,
    Critic,
)
from tianshou.exploration import GaussianNoise

import torch, numpy as np
from torch import nn
from torch._C import device


class TD3:
    """Implements the TD3 Algorithm
    """
    def __init__(
        self,
        action_space,
        state_shape,
        action_shape,
        device,
        actor_hidden_shape=[128, 128],
        critic_hidden_shape=[128, 128],
        **kwargs
    ):
        self.action_space = action_space
        self.state_shape = state_shape
        self.action_shape = action_shape
        self.actor_hidden_shape = actor_hidden_shape
        self.critic_hidden_shape = critic_hidden_shape
        self.device = device

    def __call__(
        self,
        actor_lr=0.001,
        critic_lr=0.001,
        tau=0.005,
        gamma=1.0,
        n_step=4,
        exploration_noise=0.3,
        policy_noice=0.2,
        update_actor_freq=2,
        noise_clip=0.5,
        **kwargs
    ):
        """Creates an actor and two critic nets and returns an instance of TD3 Policy initialised with them

        Args:
            actor_lr (float, optional): Learning rate for the actor. Defaults to 0.001.
             critic_lr (float, optional): Learning rate for the critic. Defaults to 0.001.
            tau (float, optional): Soft parameter for computing actions. Defaults to 0.005.
            gamma (float, optional): Discount factor. Defaults to 1.0.
            n_step (int, optional): Number of steps to look ahead. Defaults to 4.
            exploration_noise (float, optional): Sigma for gaussian noise . Defaults to 0.3.
            policy_noice (float, optional): Noise parameter for policy. Defaults to 0.2.
            update_actor_freq (int, optional): Frequency of updating actor. Defaults to 2.
            noise_clip (float, optional): Noise clipping parameter. Defaults to 0.5.

        Returns:
            Instance of TD3 Policy
        """
        actor_net = Net(
            self.state_shape,
            hidden_sizes=self.actor_hidden_shape,
            device=self.device,
        )
        actor = Actor(
            actor_net,
            self.action_shape,
            device=self.device,
        ).to(self.device)
        actor_opt = torch.optim.Adam(actor.parameters(), lr=actor_lr)

        critic_net1 = Net(
            self.state_shape,
            self.action_shape,
            hidden_sizes=self.critic_hidden_shape,
            concat=True,
            device=self.device,
        )
        critic1 = Critic(critic_net1, device=self.device).to(self.device)
        critic_opt1 = torch.optim.Adam(critic1.parameters(), lr=critic_lr)

        critic_net2 = Net(
            self.state_shape,
            self.action_shape,
            hidden_sizes=self.critic_hidden_shape,
            concat=True,
            device=self.device,
        )
        critic2 = Critic(critic_net2, device=self.device).to(self.device)
        critic_opt2 = torch.optim.Adam(critic2.parameters(), lr=critic_lr)

        return TD3Policy(
            actor,
            actor_opt,
            critic1,
            critic_opt1,
            critic2,
            critic_opt2,
            tau=tau,
            gamma=gamma,
            estimation_step=n_step,
            exploration_noise=GaussianNoise(sigma=exploration_noise),
            policy_noise=policy_noice,
            update_actor_freq=update_actor_freq,
            noise_clip=noise_clip,
            action_space=self.action_space,
        )
