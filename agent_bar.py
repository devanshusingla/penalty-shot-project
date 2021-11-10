from agents import Hardcoded_Baseline, Hardcoded_Baseline_Adaptive, move_up
from agents.device import MS

agent = MS(id="B", time_interval=0.1)
# agent = Hardcoded_Baseline_Adaptive(id = 'B')
agent.run()

# from agents.device import mouse
