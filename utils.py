import gym
from gym.spaces import Tuple, Discrete, Dict
from gym.spaces.box import Box
from gym.spaces.utils import flatten_space, unflatten
import numpy as np

# https://github.com/thu-ml/tianshou/issues/192 to enable rendering wrapper
class RenderEnvWrapper(gym.Wrapper):
    def __init__(self, env, eps: float = 0.02):
        super().__init__(env)
        self.do_render = False
        self.eps = eps

    def step(self, action):
        obs, rew, done, info = self.env.step(action)
        if done:
            eps = np.random.rand()
            if eps < self.eps:
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
        assert(k >= 3)
        self.k = k
        self._bar_action_space = Discrete(k)
        self.bar_action_space = flatten_space(self._bar_action_space)
        self.action_space = Dict({'puck': env.action_space['puck'], 'bar': self.bar_action_space})
    
    def action(self, act):
        act['bar'] = -1.0 + 2*act['bar']/(self.k-1)
        return act



def general_make_env(params):
    env = None
    if 'env' in params:
        env = gym.make('gym_env:penalty-shot-v0', **params['env'])
    else:
        env = gym.make('gym_env:penalty-shot-v0')
    if 'render' in params:
        env = RenderEnvWrapper(env, **params['render'])
    if 'flatten' in params:
        env = gym.wrappers.FlattenObservation(env)
    if 'discrete' in params:
        env = DiscreteActionWrapper(env, **params['discrete'])
    return env
