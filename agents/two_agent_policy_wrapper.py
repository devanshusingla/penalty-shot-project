import gym

from typing import List, Tuple
import tianshou as ts
from tianshou.data import Batch
from tianshou.data.buffer.base import ReplayBuffer
from tianshou.policy import BasePolicy
import numpy as np

from copy import deepcopy


class TwoAgentPolicy(BasePolicy):
    def __init__(self, policies: Tuple[BasePolicy, BasePolicy], **kwargs):
        super().__init__(**kwargs)
        (self.puck_policy, self.bar_policy) = policies

    def _partition_batch(self, batch: Batch):
        puck_batch = batch
        bar_batch = deepcopy(batch)

        if not batch["act"].is_empty():
            puck_batch["act"] = puck_batch["act"]["puck"]
            bar_batch["act"] = bar_batch["act"]["bar"]

        if isinstance(batch["rew"], np.ndarray) or (
            isinstance(batch["rew"], Batch) and not batch["rew"].is_empty()
        ):
            puck_batch["rew"] = -1.0 * puck_batch["rew"]

        return (puck_batch, bar_batch)

    """
        This function is called by collector.
    """

    def forward(
        self,
        batch: Batch,
        state=None,
        other_params: dict = {},
        **kwargs,
    ) -> Batch:

        (puck_batch, bar_batch) = self._partition_batch(batch)

        puck_out = self.puck_policy.forward(
            puck_batch, state, **(other_params.get("bar", {}))
        )
        bar_out = self.bar_policy.forward(
            bar_batch, state, **(other_params.get("puck", {}))
        )

        out = Batch(
            act=Batch(puck=puck_out.act, bar=bar_out.act),
            state=np.column_stack((puck_out.state, bar_out.state))
            if puck_out.state is not None
            else None,
            params=Batch(),
        )
        out.params = Batch(
            {
                "puck": Batch(
                    {
                        key: val
                        for key, val in puck_out.items()
                        if key not in ["act", "state"]
                    }
                ),
                "bar": Batch(
                    {
                        key: val
                        for key, val in bar_out.items()
                        if key not in ["act", "state"]
                    }
                ),
            }
        )

        return out

    def map_action(self, act):
        act["bar"] = self.bar_policy.map_action(act["bar"])
        act["puck"] = self.puck_policy.map_action(act["puck"])
        return act

    def set_eps(self, eps: float) -> None:
        """Set the eps for epsilon-greedy exploration."""
        if hasattr(self.puck_policy, "set_eps"):
            self.puck_policy.set_eps(eps)
        if hasattr(self.bar_policy, "set_eps"):
            self.bar_policy.set_eps(eps)


    """
        These three functions are called in update function of BasePolicy in the order process_fn -> learn -> post_process_fn one after another.
    """

    def process_fn(
        self, batch: Batch, buffer: ReplayBuffer, indices: np.ndarray
    ) -> Batch:
        (puck_batch, bar_batch) = self._partition_batch(batch)

        puck_out = (
            self.puck_policy.process_fn(puck_batch, buffer, indices)
            if self.puck_policy.process_fn
            else puck_batch
        )
        bar_out = (
            self.bar_policy.process_fn(bar_batch, buffer, indices)
            if self.bar_policy.process_fn
            else bar_batch
        )

        return (puck_out, bar_out)

    def learn(self, batch: Batch, **kwargs):
        (puck_batch, bar_batch) = batch
        puck_out = self.puck_policy.learn(puck_batch, **kwargs)
        bar_out = self.bar_policy.learn(bar_batch, **kwargs)

        return bar_out

    def post_process_fn(
        self, batch: Batch, buffer: ReplayBuffer, indices: np.ndarray
    ) -> None:
        if hasattr(buffer, "update_weight") and hasattr(batch, "weight"):
            buffer.update_weight(indices, batch.weight)
