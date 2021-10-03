import os
os.system('pip install -e gym-env')
import time
import gym
env = gym.make('gym_env:penalty-shot-v0')
env.reset()
env.render()
time.sleep(0.5)
for _ in range(100):
    time.sleep(0.05)
    env.render()
    state, reward, done, info = env.step(
        env.puck_action_space.sample(), 
        env.bar_action_space.sample()
        ) # take a random action
    if done:
        time.sleep(0.5)
        break
env.close()
