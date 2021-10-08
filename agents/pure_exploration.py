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