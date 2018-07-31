import numpy as np
import random
from tensorflow.contrib.training import HParams


class BaseEnv:
    def step(self, action):
        """
        Applies the action and steps simulation
        :param action: action at time-step
        :return: obs dict where:
                  -each key is an observation at that step
                  -keys are constant across entire datastep (e.x. every-timestep has 'state' key)
                  -keys corresponding to numpy arrays should have constant shape every timestep (for caching)
                  -images should be placed in the 'images' key in a (ncam, ...) array
        """
        raise NotImplementedError

    def _default_hparams(self):
        return HParams()
    
    def reset(self):
        """
        Resets the environment and returns initial observation
        :return: obs dict (look at step(self, action) for documentation)
        """
        raise NotImplementedError

    def valid_rollout(self):
        """
        Checks if the environment is currently in a valid state
        Common invalid states include:
            - object falling out of bin
            - mujoco error during rollout
        :return: bool value that is False if rollout isn't valid
        """
        raise NotImplementedError

    def goal_reached(self):
        """
        Checks if the environment hit a goal (if environment has goals)
            - e.x. if goal is to lift object should return true if object lifted by gripper
        :return: whether or not environment reached goal state
        """
        raise NotImplementedError("Environment has No Goal")

    def has_goal(self):
        """
        :return: Whether or not environment has a goal
        """
        return False

    def render(self):
        """ Renders the enviornment.
        Implements custom rendering support. If mode is:

        - dual: renders both left and main cameras
        - left: renders only left camera
        - main: renders only main (front) camera
        :param mode: Mode to render with (dual by default)
        :return: uint8 numpy array with rendering from sim
        """
        raise NotImplementedError("Rendering not implemented in Base Env")

    @property
    def adim(self):
        """
        :return: Environment's action dimension
        """
        raise NotImplementedError

    @property
    def sdim(self):
        """
        :return: Environment's state dimension
        """
        raise NotImplementedError

    def seed(self, seed=None):
        random.seed(seed)
        np.random.seed(seed)

    def eval(self):
        """
        return environment statistics, like distance to goal etc.
        :param agentdata:
        :return:
        """
        pass
