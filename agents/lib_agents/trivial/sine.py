from tianshou.data.batch import Batch
from tianshou.policy import BasePolicy
import numpy as np


class SinePolicy(BasePolicy):
    """Implements the Sine policy.

    Args:
        BasePolicy (): The base policy class
    """

    def __init__(
        self,
        max_cycles: int = 2,
        min_magnitude=0.8,
        seed: int = 0,
        max_steps: int = 90,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.rng = np.random.default_rng(seed)
        self.max_steps = (
            max_steps  # Maximum number of steps the agent will move for in each episode
        )
        self.max_cycles = max_cycles  # Maximum number of cycles
        self.min_magnitude = min_magnitude  # Minimum magnitude of the action
        self.param = {}

    def _get_action(self, info_batch: Batch, done_batch: Batch):
        """Calculates the action given the observation batch and information batch according to sine policy.

        Args:
            obs_batch (Batch): Observation Batch
            info_batch (Batch): Information Batch

        Returns:
            np.ndarray: The action array
        """
        act = np.empty(info_batch.shape[0])
        for i, (info, done) in enumerate(zip(info_batch, done_batch)):
            if info.env_id not in self.param or done:
                self.param[info.env_id] = (
                    self.min_magnitude + self.rng.random() * (1 - self.min_magnitude),
                    (2 * self.rng.random() - 1) * self.max_cycles,
                )
            act[i] = self.param[info.env_id][0] * np.sin(
                np.pi * self.param[info.env_id][1] * info.steps / self.max_steps
            )

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
            act = self._get_action(batch.info, batch.done)
        else:
            act = np.zeros(batch.obs.shape[0])
        return Batch(act=act, state=None)

    def learn(self, batch: Batch, **kwargs):
        return {}
