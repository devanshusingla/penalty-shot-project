from tianshou.data.batch import Batch
from tianshou.policy import BasePolicy
import numpy as np


class GreedyPolicy(BasePolicy):
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
        self.max_steps = max_steps
        self.agent = agent
        self.disc_k = disc_k

    def _get_action(self, obs_batch: Batch, info_batch: Batch):
        act = np.empty(info_batch.shape[0])
        for i, (info, obs) in enumerate(zip(info_batch, obs_batch)):
            if self.disc_k is not None:
                act[i] = ((obs[1] - obs[3]) + 2) * (self.disc_k - 1) / 4
                assert act[i] >= 0 and act[i] <= self.disc_k - 1

                if self.agent != "bar":
                    raise NotImplementedError
            else:
                act[i] = np.sign(obs[1] - obs[3])
                assert act[i] >= -1 and act[i] <= 1
                
                if self.agent != "bar":
                    if np.abs(obs[1]-obs[3]) < 0.005:
                        if np.abs(obs[i]) < 0.1:
                            act[i] = np.sign(obs[1])
                        else:
                            act[i] = -np.sign(obs[1])
                        if act[i] == 0: act[i] = 2*np.random.randint(2)-1
        return act

    def forward(self, batch: Batch, state=None, **kwargs):
        # print(batch)
        # print(batch.info)
        if not batch.info.is_empty():
            act = self._get_action(batch.obs, batch.info)
        else:
            act = np.zeros(batch.obs.shape[0])
        # print(act)
        return Batch(act=act, state=None)

    def learn(self, batch: Batch, **kwargs):
        return {}
