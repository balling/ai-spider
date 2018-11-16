from stack import Stock, Column
from game import Game
import util
import random
from collections import defaultdict
import math

class SpiderMDP(object):
    def __init__(self, game):
        self.game = game
    def getAgentColumns(self, game):
        agentColumns = [list() for _ in range(10)]
        hiddenNumber = [0 for _ in range(10)]
        for i, column in enumerate(game.columns):
            for card in column.cards:
                if card.face_up == True:
                    agentColumns[i].append(card)
                else:
                    hiddenNumber[i] += 1
        return tuple(agentColumns), tuple(hiddenNumber)
    def getAgentStock(self, game):
        return len(game.stock.cards)
    def getState(self, game):
        return (self.getAgentColumns(game), self.getAgentStock(game), game.score, game.completed)
    def getAction(self, game, state):
        actions = []
        # todo: optimize
        for from_stack in self.getAgentColumns(game):
            seen_empty = False
            for to_stack in self.getAgentColumns(game):
                if from_stack is to_stack:
                    continue
                pile = from_stack.getPile()
                action = None
                if not to_stack.cards:
                    if seen_empty:
                        continue
                    if len(pile) < len(from_stack.cards):
                        action = (len(pile), 'move', len(pile), from_stack, to_stack)
                    elif len(pile) > 1 and self.stock.cards:
                        action = (len(pile) - 1, 'move', len(pile) - 1, from_stack, to_stack)
                    seen_empty = True
                elif pile and to_stack.acceptsCards(pile):
                    action = (len(pile), 'move', len(pile), from_stack, to_stack)
                if action and (state + action not in game.states):
                    actions.append(action)
        if game.stock.canDealCards():
            actions.append((-1, 'deal'))
        actions.sort(reverse=True)
        return actions
    def startState(self, game):
        game.createGame((0, 0, 0, 0))
        game.startGame()
        return (self.getAgentColumns(game), self.getAgentStock(game), game.score, game.completed)

class QLearningAlgorithm(util.RLAlgorithm):
    def __init__(self, actions, discount, featureExtractor, explorationProb=0.2):
        self.actions = actions
        self.discount = discount
        self.featureExtractor = featureExtractor
        self.explorationProb = explorationProb
        self.weights = defaultdict(float)
        self.numIters = 0

    # Return the Q function associated with the weights and features
    def getQ(self, state, action):
        score = 0
        for f, v in self.featureExtractor(state, action):
            score += self.weights[f] * v
        return score

    # This algorithm will produce an action given a state.
    # Here we use the epsilon-greedy algorithm: with probability
    # |explorationProb|, take a random action.
    def getAction(self, state):
        self.numIters += 1
        if random.random() < self.explorationProb:
            return random.choice(self.actions(state))
        else:
            return max(tuple(self.getQ(state, action), action) for action in self.actions(state))[1]

    # Call this function to get the step size to update the weights.
    def getStepSize(self):
        return 1.0 / math.sqrt(self.numIters)

    # We will call this function with (s, a, r, s'), which you should use to update |weights|.
    # Note that if s is a terminal state, then s' will be None.  Remember to check for this.
    # You should update the weights using self.getStepSize(); use
    # self.getQ() to compute the current estimate of the parameters.
    def incorporateFeedback(self, state, action, reward, newState):
        q = self.getQ(state, action)
        v = 0 if newState is None else max(tuple(self.getQ(newState, nextAction), nextAction) for nextAction in self.actions(state))[0]
     n   x = self.getStepSize() * ((reward + self.discount * v) - q)
        for f, v in self.featureExtractor(state, action):
            self.weights[f] += x

# Return a single-element list containing a binary (indicator) feature
# for the existence of the (state, action) pair.  Provides no generalization.
def identityFeatureExtractor(state, action):
    featureKey = tuple(state[0], action)
    featureValue = 1
    return [(featureKey, featureValue)]


