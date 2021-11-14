from tianshou.policy.modelfree.a2c import A2CPolicy
from torch import optim
from tianshou.policy import PPOPolicy
import torch, numpy as np
from tianshou.utils.net.common import ActorCritic, Net
from tianshou.utils.net.continuous import ActorProb, Critic
from torch.distributions import Independent, Normal


def dist(*logits):
    return Independent(Normal(*logits), 1)


class PPO:
    def __init__(self, state_shape, action_space, hidden_sizes=[128, 128], **kwargs):
        self.state_shape = state_shape
        self.action_space = action_space
        self.action_shape = action_space.shape
        self.max_action = action_space.high[0]
        self.hidden_sizes = hidden_sizes

    def __call__(self, lr=1e-3, **kwargs):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        actor_net = Net(self.state_shape, hidden_sizes=self.hidden_sizes, device=device)
        actor = ActorProb(
            actor_net, self.action_shape, max_action=self.max_action, device=device
        ).to(device)
        critic = Critic(
            Net(self.state_shape, 1, hidden_sizes=self.hidden_sizes, device=device),
            device=device,
        ).to(device)
        actor_critic = ActorCritic(actor, critic)
        for m in actor_critic.modules():
            if isinstance(m, torch.nn.Linear):
                torch.nn.init.orthogonal_(m.weight)
                torch.nn.init.zeros_(m.bias)
        optim = torch.optim.Adam(actor_critic.parameters(), lr=lr)
        return PPOPolicy(
            actor=actor,
            critic=critic,
            optim=optim,
            dist_fn=dist,
            action_space=self.action_space,
            **kwargs
        )

    def __name__(self):
        return "PPO"
