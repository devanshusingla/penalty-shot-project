from tianshou.policy import DQNPolicy
import torch, numpy as np
from torch import nn


class DQN:
    class Net(nn.Module):
        def __init__(self, state_shape, action_shape):
            super().__init__()
            self.model = nn.Sequential(
                nn.Linear(np.prod(state_shape), 128),
                nn.ReLU(inplace=True),
                nn.Linear(128, 128),
                nn.ReLU(inplace=True),
                nn.Linear(128, 128),
                nn.ReLU(inplace=True),
                nn.Linear(128, np.prod(action_shape)),
            )

        def forward(self, obs, state=None, info={}):
            if not isinstance(obs, torch.Tensor):
                obs = torch.tensor(obs, dtype=torch.float)
            obs.to(self.device)
            batch = obs.shape[0]
            logits = self.model(obs.view(batch, -1))
            # print("DQN Forward:", logits.shape)
            return logits, state

    def __init__(self, state_shape, action_shape, device, lr, **kwargs):
        self.device = device
        self.net = self.Net(state_shape, action_shape).to(self.device)
        self.optim = torch.optim.Adam(self.net.parameters(), lr)

    def __call__(self, **kwargs):
        return DQNPolicy(model=self.net, optim=self.optim, **kwargs)

    def __name__(self):
        return 'DQN'
