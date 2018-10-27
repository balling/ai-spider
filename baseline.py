from infra.game import Game
import csv


def main():
    high_score = 0
    win_count = 0
    count = 10000
    try:
        with open('output/baseline-1suit.csv', 'wb') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(('ID', 'Result', 'Score', '#Moves', '#Stacks'))
            for i in range(count):
                game = Game(i)
                game.createGame((0, 0, 0, 0))
                game.startGame()
                print(game)
                moves = game.getValidMoves()
                while not game.won() and moves:
                    game.performMoves(moves[0])
                    moves = game.getValidMoves()
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
    main()
