# Communication Setup

## Setting up Server
The `PSServer` class present in `server.py` is used for creating server. It accepts Penalty Shot Environment as input and an optional input of port with its default value specified in `config.json` file. To setup a server simply create an object of `PSServer` class and run it using start command or you can directly run the `start_server.py` which starts server with default parameters for all functions.

## Connecting to Server
The `PSClient` class present in `client.py` us used for connecting with server. It accepts id of agent as input. Here id represent whether the agent is playing as puck which is given by 'P' or as bar which is given by 'B'. Simply create an object of `PSClient` class with whatever role you want to play as.

Calling its `connect` function will try to connect user to server. If position for the role is free, the agent will get connected and will recieve `(starting state, completion state)` as output otherwise it outputs `None`.

Once the agent is connected, you can give action using step function of `PSClient` object and when the state has been updated on the server you will recieve the result tuple consisting of `(new state, reward, completion state, info)`

You can close the connection in between using close function of `PSClient` object.

Sample test code for puck and bar agent have been given in `puck_connect.py` and `bar_connect.py` files. To test simply start a server if not started and in separate terminals run both these files.