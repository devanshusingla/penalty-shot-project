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


def make_render_discrete_env(render_eps, k: int = 7):
    return DiscreteActionWrapper(
        gym.wrappers.FlattenObservation(
            RenderEnvWrapper(gym.make("gym_env:penalty-shot-v0"), render_eps)
        ),
        k=k,
    )


def make_render_env(render_eps):
    return gym.wrappers.FlattenObservation(
        RenderEnvWrapper(gym.make("gym_env:penalty-shot-v0"), render_eps)
    )


def make_rew_env():
    return RewardWrapper(
        gym.wrappers.FlattenObservation(gym.make("gym_env:penalty-shot-v0"))
    )


def make_render_rew_env():
    return RenderEnvWrapper(
        RewardWrapper(
            gym.wrappers.FlattenObservation(gym.make("gym_env:penalty-shot-v0"))
        )
    )
    
def IncNegReward(obs, rew, done, info, func_params: dict = {}):
    lamda = func_params.get('lamda', 0.5)
    dist = func_params.get('dist', 0.4)
    if done and rew < 0:
        rew += lamda * max(0.0, dist - np.abs(obs[1][1] - obs[0][1]))
    return obs, rew, done, info

def AbsDifReward(obs, rew, done, info, func_params: dict = {}):
    if done:
        delta = np.sum(np.abs(np.array(obs[1], dtype=np.float32) - np.array(obs[0], dtype=np.float32)))
        rew = 1 - delta
    return obs, rew, done, info

def FourApprReward(obs, rew, done, info, func_params: dict = {}):
    # exponent = func_params.get('exponent', 4.0)
    if done:
        delta = np.sum(np.abs(np.array(obs[1], dtype=np.float32) - np.array(obs[0], dtype=np.float32)))
        rew = 2/(1 + (6*delta)**4) - 1
    return obs, rew, done, info    

def IdReward(obs, rew, done, info, func_params: dict = {}):
    return obs, rew, done, info

class RewardWrapper(gym.Wrapper):
    def __init__(self, env, reward_transform = IdReward, func_params: dict = {}):
        super().__init__(env)
        self.reward_func = reward_transform
        self.func_params = func_params

    def step(self, action):
        obs, rew, done, info = self.env.step(action)
        obs, rew, done, info = self.reward_func(obs, rew, done, info, self.func_params)
        return obs, np.reshape(rew, newshape=action.shape), done, info

def general_make_env(params={}):
    env = None
    if 'env' in params:
        env = gym.make('gym_env:penalty-shot-v0', **params['env'])
    else:
        env = gym.make('gym_env:penalty-shot-v0')
    if 'reward' in params:
        env = RewardWrapper(env, **params['reward'])
    if 'render' in params:
        env = RenderEnvWrapper(env, **params['render'])
    if 'flatten' in params:
        env = gym.wrappers.FlattenObservation(env)
    if 'discrete' in params:
        env = DiscreteActionWrapper(env, **params['discrete'])
    return env
