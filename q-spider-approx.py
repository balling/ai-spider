from infra.game import Game
from infra.util import getValidMoves
from mdp.qlearning import QLearningAlgorithm
import random, csv, pickle, math


def featureExtractor(state, action):
    features = []
    hasStock = state[0] > 0
    numCards = [len(col) for col in state[1:]]
    numFaceCards = [sum([1 for card in col if len(card)>0]) for col in state[1:]]
    if action[0] == 'move':
        _, f, t, n = action
        for i, nc in enumerate(numCards):
            if i==f:
                features.append(((hasStock, nc, numFaceCards[i], -n), 3))
            elif i==t:
                features.append(((hasStock, nc, numFaceCards[i], n), 3))
    return features

def getStepSize(numIters):
    return 1.0 / max(1, math.log10(numIters+1)-5)

def learn(rl, numTrials=300000, verbose=False):
    totalRewards = []  # The rewards we get on each trial
    wins = 0
    discount = 0.99
    for trial in range(numTrials):
        game = Game(trial)
        game.createGame((0, 0, 0, 0))
        game.startGame()
        state = game.getVisibleState()
        totalDiscount = 1
        totalReward = 0
        while not game.won():
            action = rl.getAction(state)
            if not action:
                break
            newState, reward = game.performMovesQ(action)
            if game.won():
                reward += 1000000
                wins += 1
            rl.incorporateFeedback(state, action, reward, newState)
            totalReward += reward
            totalReward += totalDiscount * reward
            totalDiscount *= discount
            state = newState
        if verbose:
            print("win ratio %d/%d = %f, state space explored: %d" % (wins, trial+1, wins/(trial+1), len(rl.weights)))
        totalRewards.append(totalReward)
        rl.resetCache()
    return totalRewards
    

def evaluate(rl):
    high_score = 0
    win_count = 0
    count = 1000
    rl.explorationProb = 0
    try:
        with open('output/qlearning-1suit-no-extra-reward.csv', 'w') as csvfile:
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
    rl = QLearningAlgorithm(getValidMoves, 0.99, featureExtractor, getStepSize=getStepSize, explorationProb=0.02)
    learn(rl, verbose=True)
    evaluate(rl)
    with open('weights-approx-no-extra-reward.pickle', 'wb') as picklefile:
        print(len(rl.weights))
        pickle.dump(rl.weights, picklefile)
    # game = Game(1)
    # game.createGame((0,0,0,0))
    # game.startGame()
    # print(game)
    # print(getValidMoves(game.getVisibleState()))
