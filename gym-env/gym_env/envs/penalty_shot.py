import gym
import numpy as np

class PSE(gym.Env):
  # Initializing environment with alpha and beta and also a seed value for random operations
  def __init__(self, mainSeed=0):
    # setting environment parameters
    self.seed(mainSeed)                               # Sets up seed and random value generators

  # Moves environment forward by 1 time step
  def step(self, action):
    state = None
    reward = None
    done = None
    info = None

    return state, reward, done, info  # returns result tuple after action is taken
  
  # Resets the environment's random generators to enable reproducability.
  def reset(self, fullReset=False):
    self.state = self.startState
    state = None
    done = None

    if fullReset:
      self.rng = np.random.default_rng(seed=self.seed)
    return state, done
  
  # Creates seeds and random generator for environment
  def seed(self, mainSeed):
    self.mainSeed = mainSeed                                                # Main seed
    self.mainRng = np.random.default_rng(seed=mainSeed)                     # Main random generator to generate other seeds
    
    self.seed = self.mainRng.integers(100000)
    self.rng = np.random.default_rng(seed=self.seed)
  
  def render(self):
    pass

  def close(self):
    pass