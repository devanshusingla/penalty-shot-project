import torch
import numpy as np
import tianshou as ts
import pprint
from tianshou.utils import WandbLogger
from tianshou.env import SubprocVectorEnv
from tianshou.data import Collector, VectorReplayBuffer
from tianshou.trainer import offpolicy_trainer, onpolicy_trainer
from agents import TwoAgentPolicy
from agents.lib_agents import *
from .envs import make_render_env, make_env, make_discrete_env, make_render_discrete_env
import argparse


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--discrete", action="store_true", default=False)
    parser.add_argument("--discrete-k", type=int, default=7)
    parser.add_argument("--eps-test", type=float, default=0.005)
    parser.add_argument("--eps-train", type=float, default=1.0)
    parser.add_argument("--eps-train-final", type=float, default=0.05)
    parser.add_argument(
        "--eps-train-decay", type=str, default="exp", choices=["exp", "lin", "const"]
    )
    parser.add_argument("--buffer-size", type=int, default=100000)
    parser.add_argument("--exploration-noise", type=bool, default=True)
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
    parser.add_argument("--test-num", type=int, default=100)
    parser.add_argument("--logdir", type=str, default="log")
    parser.add_argument("--render", type=float, default=0.0)
    parser.add_argument(
        "--device", type=str, default="cuda" if torch.cuda.is_available() else "cpu"
    )

    parser.add_argument("--wandb-save-interval", type=int, default=1)
    parser.add_argument("--wandb-project", type=str, default="test-project")
    parser.add_argument("--wandb-name", type=str, required=True)
    parser.add_argument("--wandb-entity", type=str, default="penalty-shot-project")
    parser.add_argument("--wandb-run-id", type=str, default=None)

    return parser.parse_args()


def main(args):

    print(args.device)
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

    train_envs = SubprocVectorEnv([lambda: env for _ in range(args.training_num)])
    test_envs = SubprocVectorEnv([lambda: env for _ in range(args.test_num)])

    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    train_envs.seed(args.seed)
    test_envs.seed(args.seed)

    # define policies for puck and bar here
    policy_puck = SinePolicy()
    policy_bar = SAC(
        env.action_space["bar"],
        env.observation_space.shape,
        env.action_space["bar"].shape,
        args.device,
    )(actor_lr=args.lr, critic_lr=args.lr, gamma=args.gamma, n_step=args.n_step)

    policy = TwoAgentPolicy(
        (policy_puck, policy_bar),
        observation_space=env.observation_space,
        action_space=env.action_space,
    )

    train_collector = Collector(
        policy,
        train_envs,
        VectorReplayBuffer(args.buffer_size, args.training_num),
        exploration_noise=args.exploration_noise,
    )
    test_collector = Collector(
        policy, test_envs, exploration_noise=args.exploration_noise
    )

    logger = WandbLogger(
        save_interval=args.wandb_save_interval,
        project=args.wandb_project,
        name=args.wandb_name,
        entity=args.wandb_entity,
        run_id=args.wandb_run_id,
    )

    def train_fn(epoch, env_step):
        tot_steps = args.epoch * args.step_per_epoch
        if args.eps_train_decay == "const":
            eps = args.eps_train_final
        elif args.eps_train_decay == "lin":
            eps = args.eps_train - (env_step / tot_steps) * (
                args.eps_train - args.eps_train_final
            )
        elif args.eps_train_decay == "exp":
            eps = args.eps_train * (
                (args.eps_train_final / args.eps_train) ** (env_step / tot_steps)
            )
        policy.set_eps(eps)

    def test_fn(epoch, env_step):
        policy.set_eps(args.eps_test)

    result = offpolicy_trainer(
        policy,
        train_collector,
        test_collector,
        args.epoch,
        args.step_per_epoch,
        args.step_per_collect,
        args.test_num,
        args.batch_size,
        train_fn=train_fn,
        test_fn=test_fn,
        logger=logger,
        update_per_step=args.update_per_step,
    )

    pprint.print(result)


if __name__ == "__main__":
    main(get_args())
