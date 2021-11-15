from tianshou.data.batch import Batch
from tianshou.policy import BasePolicy
import numpy as np


class RandomPolicy(BasePolicy):
    """Implements the random policy.

    Args:
        BasePolicy (): The base policy class.
    """

    def __init__(
        self, max_consecutive_steps: int, seed: int = 0, max_steps: int = 90, **kwargs
    ):
        super().__init__(**kwargs)
        self.rng = np.random.default_rng(seed)
        self.csteps = max_consecutive_steps
        self.actions = 2 * self.rng.random((max_steps // self.csteps + 1)) - 1
        self.max_steps = max_steps

    def forward(self, batch: Batch, state=None, **kwargs):
        """Calculates and forwards the action to the environment

        Args:
            batch (Batch): Current batch
            state (Any, optional): Unknown. Defaults to None.

        Returns:
            Batch: Batch containing the next action
        """
        if not batch.info.is_empty():
            act = np.array([[self.actions[s // self.csteps]] for s in batch.info.steps])
        else:
            act = np.zeros(batch.obs.shape[0])
        return Batch(act=act, state=None)

    def learn(self, batch: Batch, **kwargs):
        return {}
