from communication import PSClient
import numpy as np

class PE:
    def __init__(self, id):
        self.agent = PSClient(id=id)

    def run(self, seed=0):
        res = self.agent.connect()
        if not res:
            print("server not responding")
            return
        
        state, done = res
        print(state, done)

        rnd = np.random.default_rng(seed=seed)
        while not done:
            res = self.agent.step(2*rnd.random()-1)
            if not res:
                print("server not responding")
                break

            state, reward, done, info = res
            print(state, reward)

        self.agent.close()


class move_up:
    def __init__(self, id):
        self.agent = PSClient(id=id)

    def run(self, seed=0):
        state, done = self.agent.connect()

        while not done:
            state, reward, done, info = self.agent.step(1)
            print(state, reward)

        self.agent.close()


class move_sine:
    """
    The puck moves along a sine contour with a certain amplitude.

    ...

    Attributes :
    amplitude : The amplitude of the sine curve. Arbitrarily large amplitudes cant be achieved under the constraint that the action taken by the agent must be between [-1,1]. In such cases the action required to maintain the trajectory is calculated and clamped to lie in the interval [-1,1]
    """

    def __init__(self, id, amplitude = 1.52/(2*np.pi)):
        self.agent = PSClient(id=id)
        self.amplitude  = amplitude

    def run(self, seed=0):
        state, done = self.agent.connect()

        action = 1
        while not done:
            state, reward, done, info = self.agent.step(action)
            puck_pos, bar_pos, theta, v_ind = state
            puck_x, puck_y = puck_pos
            bar_x, bar_y = bar_pos

            action = self.amplitude*2*np.pi/(0.75+0.77) * np.cos(2*np.pi/1.52 * (puck_x + 0.75))
            action = max(-1, min(1, action))

            print(state, reward)

        self.agent.close()
