from tianshou.policy import DQNPolicy
import torch, numpy as np
from torch import nn


class DQN:
    """Implements the DQN Policy
    """
    def __init__(self, state_shape, action_shape, device, lr, **kwargs):
        self.device = device
        self.net = self.Net(state_shape, action_shape).to(self.device) # Self implemented network
        self.optim = torch.optim.Adam(self.net.parameters(), lr) # Adam optimiser

    class Net(nn.Module):
        """Neural net implementation of the DQN policy.

        Args:
            nn (Any): Base neural network
        """
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
            """Forward the action values.

            Args:
                obs (Any | torch.Tensor): Observation data
                state (Any, optional): Unknown. Defaults to None.
                info (dict, optional): Information object. Defaults to {}.

            Returns:
                Tuple: Returns logits (output of the model) and state
            """
            if not isinstance(obs, torch.Tensor):
                obs = torch.tensor(obs, dtype=torch.float)
            obs.to('cuda' if torch.cuda.is_available() else 'cpu')
            batch = obs.shape[0]
            logits = self.model(obs.view(batch, -1))
            return logits, state

    def __call__(self, **kwargs):
        """Calls the DQN policy with the net and optimiser

        Returns:
            [type]: [description]
        """
        return DQNPolicy(model=self.net, optim=self.optim, **kwargs)

    def __name__(self):
        return "DQN"
