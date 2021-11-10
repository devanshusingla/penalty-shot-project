from tianshou.data.batch import Batch
from tianshou.policy import BasePolicy
import numpy as np

class SinePolicy(BasePolicy):
    def __init__(self, max_cycles: int = 5, seed: int = 0, max_steps: int = 90, **kwargs):
        super().__init__(**kwargs)
        self.rng = np.random.default_rng(seed)
        self.max_steps = max_steps
        self.max_cycles = max_cycles
        self.param = {}
    
    def _get_action(self, info_batch: Batch, done_batch: Batch):
        act = np.empty(info_batch.shape[0])
        for i, (info, done) in enumerate(zip(info_batch, done_batch)):
            if info.env_id not in self.param or done:
                self.param[info.env_id] = (self.rng.random(), self.rng.integers(self.max_cycles)+1)
            act[i] = self.param[info.env_id][0]*np.sin(5*self.param[info.env_id][1]*info.steps/self.max_steps)
        
        return act

    def forward(self, batch: Batch, state=None, **kwargs):
        # print(batch.info)
        if not batch.info.is_empty():
            act = self._get_action(batch.info, batch.done)
        else:
            act = np.zeros(batch.obs.shape[0])
        # print(act)
        return Batch(act=act, state=None)
    
    def learn(self, batch: Batch, **kwargs):
        return {}