# Game Class Interface:
#    initial_state(self)
#       - returns an initial game state
#    is_mins_turn(self, state)
#    is_maxs_turn(self, state)
#       - indicates if it's Min/Max's turn
#    is_terminal(self, state)
#       - indicates if the game is over
#    utility(self, state)
#       - the utility value of the given state
#    actions(self, state)
#       - list actions legal in the given state
#    result(self, state, action)
#       - give the rstate resulting from the action in the given state
#    cutoff_test(self, state, depth)
#       - indicate if this state and depth is suitable to limit depth of search
#    eval(self, state)
#       - gives an indication about who might win at the state
#    congratulate(self, state):
#         - Called at the end of a game, display some text to the console.

import random as rand


class GameState(object):
    """ The GameState class stores the information about the state of the game.
        TicTacToe has a 3x3 game board, and players alternately place X or O in
        a blank cell.  

        The object has the following attributes:
            self.gameState - a dictionary with
                              keys: (row, col) 
                              values: blank, X, O
            self.blanks - a list of (row,col) tuples that are currently blanks
                        - storing this makes calculating actions a bit faster
            self.maxs_turn - a boolean value, True if it's Max's turn
                           - storing this makes deciding whose turn it is a bit faster
            self.cachedWin - a boolean value, True if one of the players has won
                           - storing this makes a few calculations a bit faster
            self.cachedWinner - if cachedWin is True, this is a Boolean (True: Win for Max)
                                None if cachedWin is False
                              - stored to make some calculations faster
            self.stringified - a unique string representation of the gameState
        """

    # make some class-wide constants available for quicker calculations
    _ablank = ' '
    _anX = 'X'
    _anO = 'O'

    def __init__(self):
        """ Create a new game state object.
        """
        # the gameState dictionary stores the position of each piece

        self.gameState = dict()
        for r in range(1, 4):
            for c in range(1, 4):
                self.gameState[r, c] = self._ablank

        # the blanks show what's left to choose from
        self.blanks = {v for v in self.gameState}

        # a boolean to store if it's Max's turn; True by default
        self.maxs_turn = True

        # if this state is a winning state, store that information
        # because it is cheaper to check once, than a bunch of times
        self.cachedWin = False

        # if cachedWin is True, then cachedWinner is a boolean
        # True means Max won; False means Min won
        self.cachedWinner = None

        # now cache the string that represents this state
        self.stringified = str(self)

    def myclone(self):
        """ Make and return an exact copy of the state.
        """
        new_state = GameState()
        for rc in self.gameState:
            new_state.gameState[rc] = self.gameState[rc]
        # copy the data not the reference
        new_state.blanks = {v for v in self.blanks}
        new_state.maxs_turn = self.maxs_turn
        new_state.cachedWin = self.cachedWin
        new_state.cachedWinner = self.cachedWinner
        new_state.stringified = self.stringified  # copy the reference not the string

        return new_state

    def display(self):
        """ Present the game state to the console.
        """
        for r in range(1, 4):
            print("+-+-+-+")
            print("|", end="")
            for c in range(1, 3):
                print(self.gameState[r, c], end="")
                print("|", end="")
            print(self.gameState[r, 3], end="")
            print("|")
        print("+-+-+-+")

    def __str__(self):
        """ Translate the board description into a string.  
            Could be used as a key for a hash table.  
            :return: A string that describes the board in the current state.
        """
        s = ""
        for r in range(1, 4):
            for c in range(1, 4):
                s += self.gameState[r, c]
        return s


class Game(object):
    """ The Game object defines the interface that is used by Game Tree Search
        implementation.  
    """

    def __init__(self, depthlimit=0):
        """ Initialization.  
        """
        self.depth_limit = depthlimit

    def initial_state(self):
        """ Return an initial state for the game.  
        """
        # the default TTTBoard constructor creates an empty board
        state = GameState()
        return state

    def is_maxs_turn(self, state):
        """ Indicate if it's Min's turn
            :return: True if it's Max's turn to play
        """
        return state.maxs_turn

    def is_mins_turn(self, state):
        """ Indicate if it's Min's turn
            :param state: a legal game state 
            :return: True if it's Min's turn to play
        """
        return not state.maxs_turn

    def is_terminal(self, state):
        """ Indicate if the game is over.
            :param state: a legal game state 
            :return: a boolean indicating if node is terminal
        """
        return state.cachedWin or len(state.blanks) == 0

    def actions(self, state):
        """ Returns all the legal actions in the given state.
            :param state: a state object
            :return: a list of actions legal in the given state
        """
        return [(state.maxs_turn, b) for b in state.blanks]

    def result(self, state, action):
        """ Return the state that results from the application of the
            given action in the given state.
            :param state: a legal game state
            :param action: a legal action in the game state
            :return: a new game state
        """
        # make a clone of this state
        new_state = state.myclone()

        # interpret the given action, as defined in self.actions()
        who, where = action

        # update the clone state, using the information in action
        new_state.blanks.remove(where)
        if who:
            new_state.gameState[where] = state._anX
        else:
            new_state.gameState[where] = state._anO

        new_state.maxs_turn = not state.maxs_turn

        # check if the move was a winning move here
        self._cache_winner(who, where, new_state)

        # now, finally, create the stringification

        new_state.stringified = str(new_state)
        return new_state

    def utility(self, state):
        """ Calculate the utility of the given state.
            :param state: a legal game state
            :return: utility of the terminal state
            In TicTacToe, we use the following:
                 1 if win for X, -1 for win for O, 0 for draw
        """
        if state.cachedWin and state.cachedWinner:
            return 1
        elif state.cachedWin and not state.cachedWinner:
            return -1
        else:
            return 0

    def cutoff_test(self, state, depth):
        """
            Check if the search should be cut-off early.
            :param state: a game state
            :param depth: the depth of the state,
                          in terms of levels below the start of search.
            :return: True if search should be cut off here.
        """
        # here we're implementing a simple cut-off.
        # In a more interesting game, you might look at the state
        # and allow a deeper search in important branches, and a shallower
        # search in boring branches.

        return self.depth_limit > 0 and depth > self.depth_limit

    def eval(self, state):
        """
            When a depth limit is applied, we need to evaluate the
            given state to estimate who might win.
            state: a legal game state
            :return: a numeric value in the range of the utility function
        """
        # in a game this simple, we don't really need eval().
        # in a more interesting game, you'd look at the board and
        # see who seems to have the advantage
        # here, we'll just return a random float in the range (-1, 1)
        # this is really quite a bad eval()!
        return rand.random()*2 - 1

    def congratulate(self, state):
        """ Called at the end of a game, display some appropriate 
            sentiments to the console.
            :param state: a legal game state
        """
        winstring = 'Congratulations, {} wins (utility: {})'
        if state.cachedWin and state.cachedWinner:
            print(winstring.format(state._anX, self.utility(state)))
        elif state.cachedWin and not state.cachedWinner:
            print(winstring.format(state._anO, self.utility(state)))
        else:
            print('Draw')

        return  # not really needed, but indicates the end of the method

    def transposition_string(self, state):
        """ Returns a unique string for the given state.
            :param state: a legal game state
        """
        return state.stringified  # because we only want to do this once

    def action_to_string(self, action):
        """ To make actions look nice when sent to the console.
            :param: action: an action as created by actions()
            :return: a string
        """
        who, (r, c) = action
        return "row {}, col {}".format(r, c)

    # all remaining methods are to assist in the calculations

    def _cache_winner(self, who, where, state):
        """ Look at the board and check if the new move was a winner.
            If we look right after a move, we can reduce the effort 
            needed to check.  We only have to look at the triplets
            passing through the move!
            :param: who
            :param: where
            :param state: a legal game state
            :return:
        """
        # where is a tuple (row, col)
        recent_r, recent_c = where

        # because we know who just moved, we only have to
        # check for wins for that player
        if who:
            token = state._anX
        else:
            token = state._anO

        # check row and column and up to 2 diagonals
        # we'll just set a flag if we find a win
        if all([state.gameState[r, recent_c] == token for r in range(1, 4)]):
            # check the column through recent_c
            won = True
        elif all([state.gameState[recent_r, c] == token for c in range(1, 4)]):
            # check the row through recent_r
            won = True
        elif recent_r == recent_c \
                and all([state.gameState[d, d] == token for d in range(1, 4)]):
            # check the down diagonal
            won = True
        elif recent_r + recent_c == 4 \
                and all([state.gameState[d, 4-d] == token for d in range(1, 4)]):
            # check the up diagonal
            won = True
        else:
            won = False

        # now use the flag to set the appropriate information in the state
        if won:
            state.cachedWin = True
            state.cachedWinner = who

        return  # not really needed, but indicates the end of the method
