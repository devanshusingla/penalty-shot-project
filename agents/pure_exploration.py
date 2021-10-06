from communication import PSClient
import numpy as np

class PE:
    def __init__(self, id):
        self.agent = PSClient(id=id)

    def run(self, seed=0):
        (state, done) = self.agent.connect()

        rnd = np.random.default_rng(seed=seed)
        while not done:
            state, reward, done, info = self.agent.step(2*rnd.random()-1)
            print(state, reward)

        self.agent.close()