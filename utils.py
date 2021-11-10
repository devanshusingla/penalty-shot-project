import gym
from gym.spaces import Tuple, Discrete, Dict
from gym.spaces.box import Box
from gym.spaces.utils import flatten_space, unflatten
import numpy as np

# https://github.com/thu-ml/tianshou/issues/192 to enable rendering wrapper
class RenderEnvWrapper(gym.Wrapper):
    def __init__(self, env):
        super().__init__(env)
        self.do_render = False

    def step(self, action):
        obs, rew, done, info = self.env.step(action)
        if done:
            eps = np.random.rand()
            if eps < 0.02:
                self.do_render = True
            else:
                self.do_render = False
                self.close()
        if self.do_render:
            self.env.render()
        return obs, rew, done, info


class DiscreteActionWrapper(gym.ActionWrapper):
    def __init__(self, env, k: int = 7):
        super().__init__(env)
        assert k >= 3
        self.k = k
        self._bar_action_space = Discrete(k)
        self.bar_action_space = flatten_space(self._bar_action_space)
        self.action_space = Dict(
            {"puck": env.action_space["puck"], "bar": self.bar_action_space}
        )

    def action(self, act):
        # act['bar'] = unflatten(self._bar_action_space, act['bar'])
        act["bar"] = -1.0 + 2 * act["bar"] / (self.k - 1)
        return act


def make_env():
    return gym.wrappers.FlattenObservation(gym.make("gym_env:penalty-shot-v0"))


def make_discrete_env(k: int = 7):
    return DiscreteActionWrapper(
        gym.wrappers.FlattenObservation(gym.make("gym_env:penalty-shot-v0")), k=k
    )


def make_render_discrete_env(k: int = 7):
    return DiscreteActionWrapper(
        gym.wrappers.FlattenObservation(
            RenderEnvWrapper(gym.make("gym_env:penalty-shot-v0"))
        ),
        k=k,
    )


def make_render_env():
    return gym.wrappers.FlattenObservation(
        RenderEnvWrapper(gym.make("gym_env:penalty-shot-v0"))
    )
