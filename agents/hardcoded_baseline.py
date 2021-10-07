from communication import PSClient
import numpy as np

class Hardcoded_Baseline:
    """
    The bar is hardcoded to try and capture the puck based on their current positions.
    The action taken by the bar is proportional to the difference in their y coordinates.

    ...

    Attributes : 
    amp_factor : The proportionality constant between action taken by bar and difference in y coordinate. The action taken is clamped to lie in the interval [-1,1]
    """


    def __init__(self, id, amp_factor = 2):
        self.agent = PSClient(id=id)
        self.amp_factor = amp_factor

    def run(self, seed=0):
        state, done = self.agent.connect()
        
        action = 1
        while not done:
            state, reward, done, info = self.agent.step(action)
            puck_pos, bar_pos, theta, v_ind = state
            puck_x, puck_y = puck_pos
            bar_x, bar_y = bar_pos

            action = self.amp_factor*(puck_y - bar_y)
            action = max(-1, min(1, action))

            print(state, reward)

        self.agent.close()

class Hardcoded_Baseline_Adaptive:
    """
    The bar is hardcoded to try and capture the puck based on their current positions.
    The action taken by the bar is proportional to the difference in their y coordinates.
    The proportionality constant is varied dynamically depending on how close the puck is to the finish line.
    """
    def __init__(self, id):
        # assert(id=='B')
        self.agent = PSClient(id=id)

    def run(self, seed=0):
        state, done = self.agent.connect()
        
        action = 1
        while not done:
            state, reward, done, info = self.agent.step(action)
            puck_pos, bar_pos, theta, v_ind = state
            puck_x, puck_y = puck_pos
            bar_x, bar_y = bar_pos

            action = (puck_y - bar_y) * ((0.75 + 0.77) / (0.77 - puck_x + 1e-6))
            action = max(-1, min(1, action))

            print(state, reward)

        self.agent.close()