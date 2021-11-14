import gym
from gym.spaces import Tuple, Discrete, Dict
from gym.spaces.box import Box
from gym.spaces.utils import flatten_space, unflatten
from gym.wrappers import FlattenObservation

import numpy as np

# https://github.com/thu-ml/tianshou/issues/192 to enable rendering wrapper
class EnvWrapper(gym.Wrapper):
    def __init__(
        self,
        env,
        render: bool = False,
        render_skip_ep: int = 100,
        discrete: dict = {},
        modified_reward: str = "exp",
    ):
        super().__init__(FlattenObservation(env))
        self.render = render
        if render:
            self.render_count = 0
            self.render_skip_ep = render_skip_ep

        self.discrete = discrete
        self.modified_reward = modified_reward
        self.agents = ["puck", "bar"]
        self.action_space = Dict(
            {
                agent: (
                    flatten_space(Discrete(self.discrete[agent]))
                    if agent in self.discrete
                    else Box(low=-1.0, high=1.0, shape=(1,), dtype=np.float32)
                )
                for agent in self.agents
            }
        )

    def step(self, action):
        for agent, k in self.discrete.items():
            if agent in self.discrete.keys():
                action[agent] = unflatten(Discrete(self.discrete[agent]), action[agent])

        obs, rew, done, info = self.env.step(action)

        if self.render:
            if self.render_count == 0:
                self.env.render()

            if done:
                if self.render_count == 0:
                    self.env.close()

                self.render_count += 1
                self.render_count %= self.render_skip_ep

        if self.modified_reward == None:
            rew = rew
        elif self.modified_reward == "exp":
            if done:
                rew = (
                    2 * np.exp(-3 * (abs(obs[0] - obs[2]) + abs(obs[1] - obs[3])) ** 2)
                    - 1
                )
        else:
            raise Exception("Unidentified reward type")

        return obs, rew, done, info


class MakeEnv:
    def __init__(self, **kwargs):
        self.args = kwargs

    def create_env(self):
        return EnvWrapper(gym.make("gym_env:penalty-shot-v0"), **self.args)


def make_envs(num_envs: int = 1, render_env_count: int = 1, **kwargs):
    envs = [MakeEnv(render=True, **kwargs) for _ in range(render_env_count)] + [
        MakeEnv(render=False, **kwargs) for _ in range(num_envs - render_env_count)
    ]
    return (envs, [env.create_env for env in envs])
