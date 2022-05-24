import Players
import Minimax as Searcher
#import AlphaBeta_Full as Searcher
import TicTacToe as Game
#import SithVRebels as Game

# to generate the table, we'll create a list for the input depths
list_of_depths = [1, 2, 3]

for depth in list_of_depths:

    print('Running depth', depth)
    # create the game, and the initial state
    game = Game.Game(depthlimit=depth)
    state = game.initial_state()

    # set up the player
    current_player = Players.VerboseComputer(game, Searcher.Minimax(game))
    current_player.ask_move(state)

    # print('Running full AlphaBeta depth', depth)
    # create the game, and the initial state
    # game = Game.Game(depthlimit=depth)
    # state = game.initial_state()

    # set up the players
    # searcher2 = Searcher2.Minimax(game)
    # current_player = Players.VerboseComputer(game, searcher2)
    # current_player.ask_move(state)
    # print('Table size:', len(searcher2.transposition_table))
