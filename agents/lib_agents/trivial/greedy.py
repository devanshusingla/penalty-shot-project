from tianshou.data.batch import Batch
from tianshou.policy import BasePolicy
import numpy as np


class GreedyPolicy(BasePolicy):
    """Implementation of the greedy policy

    Args:
        BasePolicy (): The base policy class.
    """
    def __init__(
        self,
        seed: int = 0,
        max_steps: int = 90,
        agent: str = "bar",
        disc_k: int = 7,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.rng = np.random.default_rng(seed)
        self.max_steps = max_steps # Maximum number of steps taken by the agent in an episode
        self.agent = agent # Name of the agent
        self.disc_k = disc_k # Number of pieces action has to discretized into

    def _get_action(self, obs_batch: Batch, info_batch: Batch):
        """Calculates the greedy action given the observation batch and information batch

        Args:
            obs_batch (Batch): Observation Batch
            info_batch (Batch): Information Batch

        Raises:
            NotImplementedError: When agent puck requests for action in discrete action space

        Returns:
            np.ndarray: The action array
        """
        act = np.empty(info_batch.shape[0])
        for i, (info, obs) in enumerate(zip(info_batch, obs_batch)):
            if self.disc_k is not None:
                # Normalised action directed towards the puck
                act[i] = ((obs[1] - obs[3]) + 2) * (self.disc_k - 1) / 4
                assert act[i] >= 0 and act[i] <= self.disc_k - 1

                if self.agent != "bar":
                    raise NotImplementedError
            else:
                # The bar moves towards the puck depending on which side it is on
                act[i] = np.sign(obs[1] - obs[3])
                assert act[i] >= -1 and act[i] <= 1

                if self.agent != "bar":
                # Greedy action for the puck depending on 
                # where is more open area away from bar
                    if np.abs(obs[1] - obs[3]) < 0.005:
                        if np.abs(obs[i]) < 0.1:
                            act[i] = np.sign(obs[1])
                        else:
                            act[i] = -np.sign(obs[1])
                        if act[i] == 0:
                            act[i] = 2 * np.random.randint(2) - 1
        return act

    def forward(self, batch: Batch, state=None, **kwargs):
        """Calculates and forwards the action to the environment

        Args:
            batch (Batch): Current batch
            state (Any, optional): Unknown. Defaults to None.

        Returns:
            Batch: Batch containing the next action
        """
        if not batch.info.is_empty():
            act = self._get_action(batch.obs, batch.info)
        else:
            act = np.zeros(batch.obs.shape[0])
        return Batch(act=act, state=None)

    def learn(self, batch: Batch, **kwargs):
        return {}
