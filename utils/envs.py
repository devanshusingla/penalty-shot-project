import gym
from gym.spaces import Tuple, Discrete, Dict
from gym.spaces.box import Box
from gym.spaces.utils import flatten_space, unflatten
from gym.wrappers import FlattenObservation
import matplotlib.pyplot as plt
from matplotlib import animation
import os
import numpy as np

# https://github.com/thu-ml/tianshou/issues/192 to enable rendering wrapper
class EnvWrapper(gym.Wrapper):
    """Environment Wrapper to enable rendering, dsicretising, and modifying rewards

    Args:
        gym (): Gym Wrapper Class
    """

    def __init__(
        self,
        env,
        render: bool = False,
        render_skip_ep: int = 100,
        discrete: dict = {},
        modified_reward: str = "exp",
        save_render_path: str = None
    ):
        super().__init__(FlattenObservation(env))
        self.render = render
        self.save_render_path = save_render_path
        self.frames = []
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
        """Steps into action after modifying the action and return obs,rew, done, info tuple after modifying suitably

        Args:
            action (Dict[str, float]): Dictionary of actions to step on

        Raises:
            Exception: if reward type is not identified

        Returns:
            Tuple[]: State, reward, done, info object
        """
        for agent, k in self.discrete.items():
            if agent in self.discrete.keys():
                action[agent] = unflatten(Discrete(self.discrete[agent]), action[agent])

        obs, rew, done, info = self.env.step(action)

        if self.render:
            # Enable rendering
            if not self.save_render_path:
                if self.render_count == 0:
                    self.env.render()

                if done:
                    if self.render_count == 0:
                        self.env.close()

                    self.render_count += 1
                    self.render_count %= self.render_skip_ep
            else:
                if not done:
                    self.frames.append(self.env.render(mode="rgb_array"))
                else:
                    self.env.close()

        if self.modified_reward == None:
            rew = rew
        elif self.modified_reward == "exp":
            # Transform reward to exponential reward function for the bar
            if done:
                rew = (
                    2 * np.exp(-3 * (abs(obs[0] - obs[2]) + abs(obs[1] - obs[3])) ** 2)
                    - 1
                )
        elif self.modified_reward == "puck_exp":
            # Transform the reward to exponential reward function for the puck
            if done:
                rew = (
                    2 * np.exp(-25 * (abs(obs[0] - obs[2]) + abs(obs[1] - obs[3])) ** 2)
                    - 1
                )
        else:
            raise Exception("Unidentified reward type")

        return obs, rew, done, info
    
    def save_render(self):
        plt.figure(
            figsize=(self.frames[0].shape[1] / 150.0, self.frames[0].shape[0] / 150.0), dpi=150
        )

        plt.axis("off")
        patch = plt.imshow(self.frames[0])

        def animate(i):
            patch.set_data(self.frames[i])

        anim = animation.FuncAnimation(
            plt.gcf(), animate, frames=len(self.frames), interval=1
        )

        # check if folder exists
        index = self.save_render_path.rfind("/")
        folder_name = self.save_render_path[: index + 1]
        if not os.path.isdir(folder_name):
            print("Made folder {}".format(folder_name))
            os.mkdir(folder_name)
        import matplotlib as mpl
        mpl.rcParams['animation.ffmpeg_path'] = r'D:\\Downloads1.9\\ffmpeg-2021-11-15-git-9e8cdb24cd-essentials_build\\bin\\ffmpeg.exe'
        anim.save(self.save_render_path, writer='ffmpeg', fps=60)

    def close(self):
        """Close the environment"""
        if self.render:
            if self.save_render_path:
                self.save_render()
                self.frames = []
        self.env.close()


class MakeEnv:
    """Creates enviroment with gym make"""

    def __init__(self, **kwargs):
        self.args = kwargs

    def create_env(self):
        return EnvWrapper(gym.make("gym_env:penalty-shot-v0"), **self.args)


def make_envs(num_envs: int = 1, render_env_count: int = 1, **kwargs):
    """Creates a list of environments with the first render_env_count environment allowed to render

    Args:
        num_envs (int, optional): Number of environments to create. Defaults to 1.
        render_env_count (int, optional): Number of environments allowed to render. Defaults to 1.

    Returns:
        List[Env]: List of environments
    """
    envs = [MakeEnv(render=True, **kwargs) for _ in range(render_env_count)] + [
        MakeEnv(render=False, **kwargs) for _ in range(num_envs - render_env_count)
    ]
    return (envs, [env.create_env for env in envs])
