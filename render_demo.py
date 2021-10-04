import os
os.system('pip install -e gym-env')
import time
import gym
env = gym.make('gym_env:penalty-shot-v0')
env.reset()
env.render()
time.sleep(0.5)

#highlights the motion of bar under acceleration
actions = (9*[0.8] + [0.7])*10

for _ in range(100):
    time.sleep(0.05)
    env.render()
    state, reward, done, info = env.step(
        env.puck_action_space.sample(), 
        # env.bar_action_space.sample()
        actions[_]
        ) # take a random action
    if done:
        time.sleep(0.5)
        break
env.close()