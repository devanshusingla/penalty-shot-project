from tianshou.data.batch import Batch
from tianshou.policy import BasePolicy
import numpy as np
from smurves import surgebinder
import time

class SmurvePolicy(BasePolicy):
    def __init__(
        self,
        seed: int = 0,
        max_steps: int = 90,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.rng = np.random.default_rng(time.time_ns())
        self.max_steps = max_steps
        self.param = {}

    def _get_action(self, info_batch: Batch, done_batch: Batch):
        act = np.empty(info_batch.shape[0])
        for i, (info, done) in enumerate(zip(info_batch, done_batch)):
            if info.env_id not in self.param or info.steps > 87:
                # print("inside: ", info.env_id)
                self.param[info.env_id] = self.gen_traj()
            act[i] = self.param[info.env_id][info.steps]

        return act

    def forward(self, batch: Batch, state=None, **kwargs):
        # print(batch.info)
        if not batch.info.is_empty():
            act = self._get_action(batch.info, batch.done)
            # print("changed: ", batch.info.env_id)
        else:
            act = np.zeros(batch.obs.shape[0])
        return Batch(act=act, state=None)

    def learn(self, batch: Batch, **kwargs):
        return {}

    def gen_traj(self):
        curves = surgebinder(n_curves = 1,
                     x_interval = [0.0, 91.0],
                     y_interval = [0.0, 2.0],
                     n_measure = 92,
                     direction_maximum = 50,
                     convergence_point = [0.0, 1.0])
        traj = np.array(curves)[0]
        traj[:, 1] -= 1
        actions = np.diff(traj[:, 1])
        v_p = (0.77 + 0.75) / 90
        actions /= v_p
        return actions
