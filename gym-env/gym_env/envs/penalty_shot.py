import gym
import numpy as np

class PSE(gym.Env):

  # Copied metadata from cartpole-v0
  metadata = {
        'render.modes': ['human', 'rgb_array'],
        'video.frames_per_second': 50
    }

  # Initializing environment with alpha and beta and also a seed value for random operations
  def __init__(
    self, 
    main_seed=0,
    max_episodes=90,
    puck_start =(-0.75, 0),
    bar_start = (0.75, 0),
    screen_size=(480, 640),
    goal_nrm = 0.77,
    bar_size=(1/6, 1/128),
    puck_diameter=1/64
    ):
    """Penalty Shot Environment

    Args:
        mainSeed (int, optional): main seed for RNG Defaults to 0.
        maxEpisodes (int, optional): Maximum number of episodes. Defaults to 90.
        puck_start (tuple, optional): Normalised start (x, y) coordinates for the puck. Defaults to (-0.75, 0).
        bar_start (tuple, optional): Normalised start (x, y) coordinates for the bar. Defaults to (0.75, 0).
        screen_size (tuple, optional): Actual screen size (height, width). Defaults to (480, 640).
        goal_nrm (float, optional): Normalised x-coordinate defining the goal line. Defaults to 0.77.
        bar_size (tuple, optional): Normalised values for size of the bar (length, width). Defaults to (1/6, 1/128).
        puck_diameter (float, optional): Normalised diameter of the puck. Defaults to 1/64.
    """
    # setting environment parameters
    self.seed(main_seed)  # Sets up seed and random value generators
    self.max_episodes = max_episodes
    self.puck_start = puck_start
    self.bar_start = bar_start
    self.screen_height,self.screen_width = screen_size
    self.goal_nrm = 0.77
    self.bar_length, self.bar_width = bar_size
    self.puck_diameter = 1/64

    self.state = None
    self.viewer = None # Rendering object

    self.v_ind = 0 # Indicator variable used to check whether the bar can accelerate in next step
    self.theta = 1
    self.startState = (self.puck_start, self.bar_start)
    self.v_p = (self.goal_nrm - self.puck_start[0])/self.max_episodes
    self.bar_action_space = gym.spaces.Box(low=np.array([-1.0]), high=np.array([1.0]), dtype=np.float32)
    self.puck_action_space = gym.spaces.Box(low=np.array([-1.0]), high=np.array([1.0]), dtype=np.float32)                    

  # Moves environment forward by 1 time step
  def step(self, puck_action: float, bar_action: float):
    """Take one step in the common environment

    Args:
        puck_action (float): Action for the puck. u_t_p in [-1, 1]
        bar_action (float): Action for the bar. u_t_b in [-1, 1]

    Returns:
        State: Current state of the environment
        Reward: Reward for both puck and bar (puck, bar)
        Done: If the episode is over
        Info: Dictionary of indicator variable and theta parameter
    """
    reward = (0, 0)
    done = False
    info = None
    puck_pos, bar_pos = self.state

    ## Update puck position
    puck_x, puck_y = puck_pos
    puck_x += self.v_p
    puck_y += self.v_p*puck_action
    puck_y = min(max(puck_y, -1), 1)

    ## Update bar position
    bar_x, bar_y = bar_pos
    v_w = 2*self.v_p*self.theta/3
    bar_y = max(min(bar_y + v_w*bar_action, 1), -1)

    # Updating indicator variable
    if (bar_action > 0):
      if self.v_ind > 0:
        self.v_ind = min(3, self.v_ind + 1)
      else:
        self.v_ind = -1
    else:
      if self.v_ind < 0:
        self.v_ind = max(-3, self.v_ind - 1)
      else:
        self.v_ind = 1

    # Updating theta
    if np.abs(self.v_ind) == 3:
      self.theta += 0.85
    else:
      self.theta = 1

    # Termination Condition
    if self.goal_nrm - (puck_x + self.puck_diameter/2) < 0.001:
      # Puck hits goal
      reward = (1, -1) # Negative reward for bar and positive for puck
      done = True
    elif (
      abs(bar_x - puck_x) < (self.puck_diameter + self.bar_width)/2 
      and abs(bar_y - puck_y) < (self.puck_diameter + self.bar_length)/2
      ):
      # Bar stopped puck
      reward = (-1, 1) # Positive reward for bar and Negative for puck
      done = True

    self.state = ((puck_x, puck_y), (bar_x, bar_y))
    info = {
      "v_ind":self.v_ind,
      "theta": self.theta
    }

    return self.state, reward, done, info  # returns result tuple after action is taken
  
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

  
  def bar_vertices(self, bar_pos):
    bar_x, bar_y = bar_pos
    l, r = (bar_x - self.bar_width/2, bar_x + self.bar_width/2) # Left, right x coordinates
    t, b = (bar_y - self.bar_length/2, bar_y + self.bar_length/2) # Top, bottom y coordinates
    # Note that the y-axis is inverted in rendering
    #  as smaller values of y lies on top

    # Scaling l, r values
    l = (l+1)*self.screen_width/2
    r = (r+1)*self.screen_width/2
    t = (t+1)*self.screen_height/2
    b = (b+1)*self.screen_height/2

    return [(l, b), (l, t), (r, t), (r, b)]

  def render(self, mode='human'):
    """Renders a view of the current state of the environment.

    Args:
        mode (str, optional): Mode of rendering environment. Defaults to 'human'.
    """

    if self.viewer is None:
            from gym.envs.classic_control import rendering

            ## Initialise screen viewer object
            self.viewer = rendering.Viewer(self.screen_width, self.screen_height)
            
            puck_pos, bar_pos = self.state

            ## Initialise bar geometry object
            bar = rendering.FilledPolygon(self.bar_vertices(bar_pos))
            bar.set_color(.93, .2, .13) # Reddish orange color
            self.bartrans = rendering.Transform()
            bar.add_attr(self.bartrans)
            self.viewer.add_geom(bar)

            self._bar_geom = bar

            ## Initialise puck geometry object
            puck_x, puck_y = puck_pos
            puck = rendering.make_circle(self.puck_diameter*self.screen_width/2)
            self.pucktrans = rendering.Transform(translation=((puck_x+1)*self.screen_width/2, (puck_y+1)*self.screen_height/2))
            puck.add_attr(self.pucktrans)
            puck.set_color(.5, .5, .8)
            self.viewer.add_geom(puck)

            ## Initialise goal line object
            goal_x = (self.goal_nrm+1)*self.screen_width/2
            goal = rendering.Line((goal_x, 0), (goal_x, self.screen_height))
            self.viewer.add_geom(goal)
            
    if self.state is None:
        return None

    puck_pos, bar_pos = self.state

    ## Update bar position
    bar = self._bar_geom
    bar.v = self.bar_vertices(bar_pos)

    ## Update puck position
    puck_x, puck_y = puck_pos
    self.pucktrans.set_translation((puck_x+1)*self.screen_width/2, (puck_y+1)*self.screen_height/2)

    return self.viewer.render(return_rgb_array=mode == 'rgb_array')

  def close(self):
    if self.viewer:
      self.viewer.close()
      self.viewer = None