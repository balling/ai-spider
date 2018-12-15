# modified from https://github.com/rgilman33/baselines-A2C/blob/master/envs.py
import os
import gym
from gym.spaces.box import Box

try:
    import pybullet_envs
except ImportError:
    pass


def make_env(env_id, seed, rank, log_dir):
    def _thunk():
        env = gym.make(env_id)
        env.seed(seed + rank)
    return _thunk


class WrapPyTorch(gym.ObservationWrapper):
    def __init__(self, env=None):
        super(WrapPyTorch, self).__init__(env)
        self.observation_space = Box(0.0, 1.0, [1, 84, 84])

    def _observation(self, observation):
        return observation.transpose(2, 0, 1)