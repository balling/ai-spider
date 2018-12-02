import collections
import random
import math

def getStepSize(numIters):
    return 1.0 / math.sqrt(numIters)

class QLearningAlgorithm():
    def __init__(self, actions, discount, featureExtractor, explorationProb=0.2, getStepSize=getStepSize):
        self.actions = actions
        self.discount = discount
        self.featureExtractor = featureExtractor
        self.explorationProb = explorationProb
        self.weights = collections.defaultdict(float)
        self.numIters = 0
        self.cache = collections.defaultdict(set)
        self.getStepSize = getStepSize

    # Return the Q function associated with the weights and features
    def getQ(self, state, action):
        score = 0
        for f, v in self.featureExtractor(state, action):
            score += self.weights[f] * v
        return score

    def resetCache(self):
        self.cache = collections.defaultdict(set)
    
    # This algorithm will produce an action given a state.
    # Here we use the epsilon-greedy algorithm: with probability
    # |explorationProb|, take a random action.
    def getAction(self, state):
        self.numIters += 1
        actions = list(set(self.actions(state)).difference(self.cache[state])) # otherwise might go into infinite loop
        if len(actions)==0:
            return None
        choice = random.choice(actions) if random.random() < self.explorationProb \
            else max((self.getQ(state, action), action) for action in actions)[1]
        self.cache[state].add(choice)
        return choice

    # We will call this function with (s, a, r, s'), which you should use to update |weights|.
    # Note that if s is a terminal state, then s' will be None.  Remember to check for this.
    # You should update the weights using self.getStepSize(); use
    # self.getQ() to compute the current estimate of the parameters.
    def incorporateFeedback(self, state, action, reward, newState):
        eta = self.getStepSize(self.numIters)
        q = self.getQ(state, action)
        v = 0
        if newState:
            actions = self.actions(newState)
            if actions:
                v = max(self.getQ(newState, a) for a in actions)
        scalar = eta * (q - (reward + self.discount * v))
        for feature, value in self.featureExtractor(state, action):
            self.weights[feature] = self.weights.get(
                feature, 0) - scalar * value

