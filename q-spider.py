from infra.game import Game
from infra.util import getValidMoves
from mdp.qlearning import QLearningAlgorithm
import random
import csv


def identityFeatureExtractor(state, action):
    featureKey = (state, action)
    featureValue = 1
    return [(featureKey, featureValue)]


def learn(rl, numTrials=50000, verbose=False):
    totalRewards = []  # The rewards we get on each trial
    for trial in range(numTrials):
        game = Game(trial)
        game.createGame((0, 0, 0, 0))
        game.startGame()
        state = game.getVisibleState()
        #totalDiscount = 1
        totalReward = 0
        while not game.won():
            action = rl.getAction(state)
            if not action:
                print('lost')
                break
            newState, reward = game.performMovesQ(action)
            rl.incorporateFeedback(state, action, reward, newState)
            totalReward += reward
            #totalReward += totalDiscount * reward
            #totalDiscount *= discount
            state = newState
        if verbose:
            print("Trial %d, (totalReward = %s)" %
                  (trial, totalReward))
        totalRewards.append(totalReward)
        rl.resetCache()
    return totalRewards
    

def evaluate(rl):
    high_score = 0
    win_count = 0
    count = 10000
    rl.explorationProb = 0
    try:
        with open('output/qlearning-1suit.csv', 'w') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(('ID', 'Result', 'Score', '#Moves', '#Stacks'))
            for i in range(count):
                rl.resetCache()
                game = Game(i)
                game.createGame((0, 0, 0, 0))
                game.startGame()
                print(game)
                while not game.won():
                    state = game.getVisibleState()
                    move = rl.getAction(state)
                    if not move:
                        break
                    game.performMovesQ(move)
                if game.won():
                    high_score = max(high_score, game.score)
                    win_count += 1
                print('Game#%d [%s] Score: %d   Moves: %d   Completed: %d' %
                      (game.id, 'Won' if game.won() else 'Lost', game.score, game.moves, game.completed))
                writer.writerow(map(str, (game.id, 'Won' if game.won()
                                          else 'Lost', game.score, game.moves, game.completed)))
    except KeyboardInterrupt:
        pass
    print('Won %d/%d games, high score is %d' % (win_count, count, high_score))


if __name__ == "__main__":
    rl = QLearningAlgorithm(getValidMoves, 1, identityFeatureExtractor)
    learn(rl, verbose=True)
    evaluate(rl)
    # game = Game(1)
    # game.createGame((0,0,0,0))
    # game.startGame()
    # print(game)
    # print(getValidMoves(game.getVisibleState()))
