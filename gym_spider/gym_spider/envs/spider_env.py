import gym
import numpy as np
import torch
from gym import error, spaces, utils
from gym.utils import seeding
from .game import Game
from .util import getValidMoves

class SpiderEnv(gym.Env):
    metadata = {'render.modes': ['human']}
    
    def __init__(self):
        self.action_space = spaces.Discrete(1081)
        self.observation_space = spaces.Box(low=-1, high=104, dtype=np.uint8, shape=(141,))
        self.seed()
        self.reset()
    
    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]
    
    def _get_obs(self):
        return torch.FloatTensor(self.game.getStateForDQN())
    
    def step(self, action):
        """

        Parameters
        ----------
        action :

        Returns
        -------
        ob, reward, episode_over, info : tuple
            ob (object) :
                an environment-specific object representing your observation of
                the environment.
            reward (float) :
                amount of reward achieved by the previous action. The scale
                varies between environments, but the goal is always to increase
                your total reward.
            episode_over (bool) :
                whether it's time to reset the environment again. Most (but not
                all) tasks are divided up into well-defined episodes, and done
                being True indicates the episode has terminated. (For example,
                perhaps the pole tipped too far, or you lost your last life.)
            info (dict) :
                 diagnostic information useful for debugging. It can sometimes
                 be useful for learning (for example, it might contain the raw
                 probabilities behind the environment's last state change).
                 However, official evaluations of your agent are not allowed to
                 use this for learning.
        """
        action = action.item()
        assert self.action_space.contains(action)
        moves = getValidMoves(self.game.getVisibleState())
        valid_actions = [1080 if move==('deal',) else (move[1]*9+move[2]-(move[1]<move[2]))*12+move[3]-1 for move in moves]
        if action not in valid_actions:
            over = self.game.won() or not len(moves)
            return self._get_obs(), 0, over, dict()
        score = self.game.score
        self.game.performMovesForDQN(action)
        over = self.game.won() or not len(getValidMoves(self.game.getVisibleState()))
        return self._get_obs(), self.game.score - score, over, dict()
    
    def reset(self):
        self.game = Game(0, self.np_random)
        self.game.createGame((0, 0, 0, 0))
        self.game.startGame()
        return self._get_obs()
    
    def render(self, mode='human', close=False):
        pass