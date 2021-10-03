import gym
import numpy as np
import math

class PSE(gym.Env):

  # Copied metadata from cartpole-v0
  metadata = {
        'render.modes': ['human', 'rgb_array'],
        'video.frames_per_second': 50
    }

  # Initializing environment with alpha and beta and also a seed value for random operations
  def __init__(self, mainSeed=0):
    # setting environment parameters
    self.seed(mainSeed)  # Sets up seed and random value generators
    self.max_episodes = 90
    self.puck_start_x_nrm = -0.75
    self.puck_start_y_nrm = 0
    self.bar_start_x_nrm = 0.75
    self.bar_start_y_nrm = 0       
    self.screen_height = 480
    self.screen_width = 640
    self.goal_nrm = 0.77
    self.state = None
    self.viewer = None


    self.puck_start = (self.puck_start_x_nrm, self.puck_start_y_nrm)
    self.bar_start = (self.bar_start_x_nrm, self.bar_start_y_nrm) 
    self.v_ind_start = 0
    self.theta_start = 1
    self.startState = (self.puck_start, self.bar_start, self.v_ind_start, self.theta_start)
    self.v_p = (self.goal_nrm - self.puck_start_x_nrm)/self.max_episodes
    self.action_space = gym.spaces.Box(low=np.array([-1.0]), high=np.array([1.0]), dtype=np.float32)                    

  # Moves environment forward by 1 time step
  def step(self, action):
    state = self.state
    reward = 0
    done = False
    info = None
    puck_pos, bar_pos, v_ind, theta = self.state

    ## Update puck position
    puck_x, puck_y = puck_pos
    puck_x += self.v_p
    puck_y += self.v_p*self.rng.uniform(-1, 1)
    puck_y = min(max(puck_y, -1), 1)

    ## Update bar position
    bar_x, bar_y = bar_pos
    v_w = 2*self.v_p*theta/3
    bar_y = max(min(bar_y + v_w*action, 1), -1)
    if (action > 0):
      v_ind = min(3, v_ind + 1)
    else:
      v_ind = max(-3, v_ind - 1)
    if np.abs(v_ind) == 3:
      theta += 0.85
    else:
      theta = 1

    self.state = ((puck_x, puck_y), (bar_x, bar_y), v_ind, theta)

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
  
  def render(self, mode='human'):
    
    puck_diameter = self.screen_width/64
    bar_width = 1/128
    bar_length = 1/6

    if self.viewer is None:
            from gym.envs.classic_control import rendering

            ## Initialise screen viewer object
            self.viewer = rendering.Viewer(self.screen_width, self.screen_height)
            
            puck_pos, bar_pos, _, _ = self.state
            ## Initialise bar geometry object
            bar_x, bar_y = bar_pos
            l, r = (bar_x - bar_width/2, bar_x + bar_width/2)
            l = (l+1)*self.screen_width/2
            r = (r+1)*self.screen_width/2
            t, b = (bar_y - bar_length/2, bar_y + bar_length/2)
            t = (t+1)*self.screen_height/2
            b = (b+1)*self.screen_height/2
            bar = rendering.FilledPolygon([(l, b), (l, t), (r, t), (r, b)])
            bar.set_color(.8, .6, .4)
            self.bartrans = rendering.Transform()
            bar.add_attr(self.bartrans)
            self.viewer.add_geom(bar)

            self._bar_geom = bar

            ## Initialise puck geometry object
            puck_x, puck_y = puck_pos
            puck = rendering.make_circle(puck_diameter/2)
            self.pucktrans = rendering.Transform(translation=((puck_x+1)*self.screen_width/2, (puck_y+1)*self.screen_height/2))
            puck.add_attr(self.pucktrans)
            puck.set_color(.5, .5, .8)
            self.viewer.add_geom(puck)

            ## Initialise goal line
            goal_x = (self.goal_nrm+1)*self.screen_width/2
            goal = rendering.Line((goal_x, 0), (goal_x, self.screen_height))
            self.viewer.add_geom(goal)
            

    if self.state is None:
        return None


    puck_pos, bar_pos, _, _ = self.state
    ## Update bar position
    bar = self._bar_geom
    bar_x, bar_y = bar_pos
    l, r = (bar_x - bar_width/2, bar_x + bar_width/2)
    l = (l+1)*self.screen_width/2
    r = (r+1)*self.screen_width/2
    t, b = (bar_y - bar_length/2, bar_y + bar_length/2)
    t = (t+1)*self.screen_height/2
    b = (b+1)*self.screen_height/2
    bar.v = [(l, b), (l, t), (r, t), (r, b)]

    ## Update puck position
    puck_x, puck_y = puck_pos
    self.pucktrans.set_translation((puck_x+1)*self.screen_width/2, (puck_y+1)*self.screen_height/2)

    return self.viewer.render(return_rgb_array=mode == 'rgb_array')

  def close(self):
    if self.viewer:
      self.viewer.close()
      self.viewer = None