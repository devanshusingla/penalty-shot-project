import gym
from gym.spaces import Tuple, Discrete
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
    def __init__(self, env, k: int = 3):
        super().__init__(env)
        assert(k >= 3)
        self.k = k
        self._action_space = Tuple((Box(low=-1.0, high=1.0, shape=(1,), dtype=np.float32), Discrete(k)))
        self.action_space = flatten_space(self._action_space)
    
    def action(self, act):
        print(act)
        print(self.action_space)
        print(self._action_space)
        act = unflatten(self._action_space, act)
        act[1] = -1.0 + 2*act[1]/(self.k-1)
        return act

def make_env():
    return gym.wrappers.FlattenObservation(gym.make('gym_env:penalty-shot-v0'))

def make_discrete_env():
    return gym.wrappers.FlattenObservation(DiscreteActionWrapper(gym.make('gym_env:penalty-shot-v0')))

def make_render_discrete_env():
    return gym.wrappers.FlattenObservation(RenderEnvWrapper(DiscreteActionWrapper(gym.make('gym_env:penalty-shot-v0'))))

def make_render_env():
    return gym.wrappers.FlattenObservation(RenderEnvWrapper(gym.make('gym_env:penalty-shot-v0')))