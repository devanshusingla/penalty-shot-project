from numpy.random.mtrand import seed
from client import PSClient
import numpy as np

a = PSClient(id='P')
(state, done) = a.connect()

rnd = np.random.default_rng(seed=0)
while not done:
    state, reward, done, info = a.step(2*rnd.random()-1)
    print(state, reward)

a.close()