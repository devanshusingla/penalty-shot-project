# Penalty Shot Project

## Game Environment
It consists of a puck and a bar with puck moving towards bar at constant horizontal speed. Both of them are controlled by separate agents. The goal of puck is to move past bar and reach final line while the goal of bar is to catch puck before it can reach final line.

The environment has been developed using gym library which accepts two action parameters corresponding to puck and bar, and moves the game by one time step giving output a tuple of state, reward, completion state and info. [See code](gym-env)

## Communication setup for agents with environment
To support asynchronous inputs from agents, we have created a main server which controls the environment. The agents using client class to connect to the server and use its step function to give their action and recieve corresponding result tuple. The server takes actions from the agents as input and synchronizes them and updates the environment by one time step. [See code](communication)

## Agents
Some common RL algorithm like only exploration have been encoded as agents for puck and bar in separate folders. The device folder contains support for input devices (keyboard, joystick) so that game can be played by a user directly. [See code](agents)