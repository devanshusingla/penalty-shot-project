from tianshou.policy import SACPolicy
from tianshou.utils.net.common import Net
from tianshou.utils.net.continuous import (
    Actor,
    ActorProb,
    Critic,
    RecurrentActorProb,
    RecurrentCritic,
)
from tianshou.exploration import GaussianNoise

import torch, numpy as np
from torch import nn
from torch._C import device


class SAC:
    """Implementation of SAC Policy
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
        self.noise = GaussianNoise(sigma=0.3)

    def __call__(
        self,
        actor_lr=0.001,
        critic_lr=0.001,
        tau=0.005,
        gamma=1.0,
        n_step=4,
        recurrent=False,
        **kwargs
    ):
        """Creates an actor and two critic nets and returns an instance of SAC Policy initialised with them

        Args:
            actor_lr (float, optional): Learning rate for the actor. Defaults to 0.001.
            critic_lr (float, optional): Learning rate for the critic. Defaults to 0.001.
            tau (float, optional): Soft parameter for computing actions. Defaults to 0.005.
            gamma (float, optional): Discount factor. Defaults to 1.0.
            n_step (int, optional): Number of steps to look ahead. Defaults to 4.
            recurrent (bool, optional): Whether to use recurrent implementation. Defaults to False.

        Returns:
            Instance of SAC Policy
        """
        if recurrent:
            actor = RecurrentActorProb(
                len(self.actor_hidden_shape),
                self.state_shape,
                self.action_shape,
                unbounded=True,
                hidden_layer_size=self.actor_hidden_shape[0],
                device=self.device,
            ).to(self.device)
        else:
            actor_net = Net(
                self.state_shape,
                hidden_sizes=self.actor_hidden_shape,
                device=self.device,
            )
            # Initialize the actor network with random weights and biases

            actor = ActorProb(
                actor_net,
                self.action_shape,
                self.actor_hidden_shape,
                unbounded=False,
                device=self.device,
            ).to(self.device)
        actor_opt = torch.optim.Adam(actor.parameters(), lr=actor_lr)

        if recurrent:
            critic1 = RecurrentCritic(
                len(self.critic_hidden_shape),
                self.state_shape,
                self.action_shape,
                hidden_layer_size=self.critic_hidden_shape[0],
                device=self.device,
            ).to(self.device)
        else:
            critic_net1 = Net(
                self.state_shape,
                self.action_shape,
                hidden_sizes=self.critic_hidden_shape,
                concat=True,
                device=self.device,
            )
            critic1 = Critic(critic_net1, device=self.device).to(self.device)
        critic_opt1 = torch.optim.Adam(critic1.parameters(), lr=critic_lr)

        if recurrent:
            critic2 = RecurrentCritic(
                len(self.critic_hidden_shape),
                self.state_shape,
                self.action_shape,
                hidden_layer_size=self.critic_hidden_shape[0],
                device=self.device,
            ).to(self.device)
        else:
            critic_net2 = Net(
                self.state_shape,
                self.action_shape,
                hidden_sizes=self.critic_hidden_shape,
                concat=True,
                device=self.device,
            )
            critic2 = Critic(critic_net2, device=self.device).to(self.device)
        critic_opt2 = torch.optim.Adam(critic2.parameters(), lr=critic_lr)

        target_entropy = -np.prod(self.action_shape)
        log_alpha = torch.zeros(1, requires_grad=True, device=self.device)
        alpha_optim = torch.optim.Adam([log_alpha], lr=3e-4)
        alpha = (target_entropy, log_alpha, alpha_optim)

        return SACPolicy(
            actor,
            actor_opt,
            critic1,
            critic_opt1,
            critic2,
            critic_opt2,
            tau=tau,
            gamma=gamma,
            alpha=alpha,
            estimation_step=n_step,
            exploration_noise=self.noise,
            action_space=self.action_space,
        )
