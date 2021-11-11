import torch
import numpy as np
import tianshou as ts
from tianshou.utils import WandbLogger
from agents import TwoAgentPolicy
from agents.lib_agents import *
from utils import make_render_env, make_env, make_discrete_env, make_render_discrete_env
import argparse


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--discrete", action="store_true", default=False)
    parser.add_argument("--discrete-k", type=int, default=7)
    parser.add_argument("--eps-test", type=float, default=0.005)
    parser.add_argument("--eps-train", type=float, default=1.0)
    parser.add_argument("--eps-train-final", type=float, default=0.05)
    parser.add_argument("--buffer-size", type=int, default=100000)
    parser.add_argument("--lr", type=float, default=0.0001)
    parser.add_argument("--gamma", type=float, default=0.99)
    parser.add_argument("--n-step", type=int, default=3)
    parser.add_argument("--target-update-freq", type=int, default=500)
    parser.add_argument("--epoch", type=int, default=100)
    parser.add_argument("--step-per-epoch", type=int, default=100000)
    parser.add_argument("--step-per-collect", type=int, default=10)
    parser.add_argument("--update-per-step", type=float, default=0.1)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--training-num", type=int, default=10)
    parser.add_argument("--test-num", type=int, default=10)
    parser.add_argument("--logdir", type=str, default="log")
    parser.add_argument("--render", type=float, default=0.0)
    parser.add_argument(
        "--device", type=str, default="cuda" if torch.cuda.is_available() else "cpu"
    )
    return parser.parse_args()


def main(args):

    # create env
    if args.discrete:
        if args.render > 0:
            env = make_render_discrete_env(args.render, args.discrete_k)
        else:
            env = make_discrete_env(args.discrete_k)
    else:
        if args.render > 0:
            env = make_render_env(args.render)
        else:
            env = make_env()
    args.state_shape = env.observation_space.shape
    args.action_shape = env.action_space.shape
    # print("Observations shape:", env.observation_space, args.state_shape)
    # print("Actions shape:", env.action_space, args.action_shape)


if __name__ == "__main__":
    main(get_args())
