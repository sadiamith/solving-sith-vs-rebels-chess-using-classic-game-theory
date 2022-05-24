import Players

# there's no reason not to use full-featured AlphaBeta as the player here; given the same depth limit
# Minimax would play just as well, but would take WAY longer
# this player will take the first move in whatever the game is
import AlphaBeta_Full as Searcher1
import AlphaBeta_Full as Searcher2

import TicTacToe as Game
#import SithVRebels as Game

# create a list of all the tuples of depth-pairs that we want to try for player 1 and player 2
list_of_depths = [(1, 1)]

for depth1, depth2 in list_of_depths:
    # create the game, and the initial state

    game1 = Game.Game(depthlimit=depth1)
    game2 = Game.Game(depthlimit=depth2)
    state = game1.initial_state()

    # set up the players
    current_player = Players.SilentComputer(game1, Searcher1.Minimax(game1))
    other_player = Players.SilentComputer(game2, Searcher2.Minimax(game2))

    # I don't think it matters which game is used
    # but this ensures no cross talk in case I have a bug somewhere
    current_game, other_game = game1, game2

    # play the game
    while not current_game.is_terminal(state):

        # ask the current player for a move
        choice = current_player.ask_move(state)

        # check the move
        assert choice in current_game.actions(
            state), "The action <{}> is not legal in this state".format(choice)

        # apply the move
        state = current_game.result(state, choice)

        # swap the players
        current_player, current_game, other_player, other_game = other_player, other_game, current_player, current_game

    # game's over
    print('For trial', depth1, depth2, end=': ')
    game1.congratulate(state)

# eof
