# The Game Class encodes the rules of a game.
# Game Class Interface:
#    initial_state(self)
#       - returns an initial game state
#       - the state can be any object that stores the details
#         needed to keep track of the game, including any information
#         convenient to store
#
#    is_mins_turn(self, state)
#    is_maxs_turn(self, state)
#       - return a boolean that indicates if it's Min/Max's turn
#
#    is_terminal(self, state)
#       - return a boolean that indicates if the state represents
#         a true end of the game situation, i.e, a win or a draw
#
#    utility(self, state)
#       - return the utility value of the given terminal state
#       - must return one of three values: k_min, k_draw, k_max
#           k_min: the value returned if Min is the winner
#           k_max: the value returned if Max is the winner
#           k_draw: the value returned if the game ends in a draw
#           - any range is allowed.
#           - probably best if k_min < k_draw < k_max
#             and k_draw half way between k_min, k_max
#       - will only be called if the state is determined to be
#         a terminal state by is_terminal()
#       - only terminal states have utility; other states get
#         their value from searching.
#
#    actions(self, state)
#       - returns a list of actions legal in the given state
#
#    result(self, state, action)
#       - returns the state resulting from the action in the given state
#
#    cutoff_test(self, state, depth)
#       - returns a bolean that indicates if this state and depth is suitable
#         to limit depth of search.  A simple implementation might just look
#         at the depth; a more sophisticated implementation might look at
#         the state as well as the depth.
#
#    eval(self, state)
#       - returns a numeric value that estimates the minimax value of the
#         given state.  This gets called if cutoff_test() returns true.
#         Instead of searching to the bottom of the tree, this function
#         tries to guess who might win.  The function should return a value
#         that is in the range defined by utility().  Because this is an
#         estimate, values close to k_min (see utility()) indicate that
#         a win for Min is likely, and values close to k_max should indicate
#         a win for Max is likely.  Should not return values outside the range
#         (k_min, k_max).  k_min means "Min wins"; a value smaller than k_min
#         makes no sense.  An estimate from eval() cannot be more extreme than a
#         fact known from utility().
#
#    transposition_string(self)
#       - return a string representation of the state
#       - for use in a transposition table
#       - this string should represent the state exactly, but also without
#         too much waste.  In a normal game, lots of these get stored!
#
#    congratulate(self)
#       - could be called at the end of the game to indicate who wins
#       - this is not absolutely necessary, but could be informative

class GameState(object):
    """ The GameState class stores the information about the state of the game.
    """

    def __init__(self, dim=5):
        # makes bigger boards a little less trouble to use
        self.dim = dim

        # a list for all the sith pieces
        self.sith = []

        # a list for all the rebel pieces
        self.rebels = []

        # a list of the jedi
        self.jedi = []

        # a boolean to store if it's Max's turn; True by default
        self.maxs_turn = True

        # if this state is a winning state, store that information
        # because it is cheaper to check once, than a bunch of times
        self.cachedTerminal = False

        # if cachedTerminal is True:
        #       cachedOutcome == True means Max won;
        #       cachedOutcome == False means Min won
        #       cachedOutcome == None means a draw
        self.cachedOutcome = None

        # now cache the string that represents this state
        self.stringified = str(self)

        self.moves_made = 0

    def myclone(self):
        """ Make and return an exact copy of the state.
        """
        new_state = GameState()

        # make copies, not references
        new_state.sith = [s for s in self.sith]
        new_state.rebels = [r for r in self.rebels]
        new_state.jedi = [j for j in self.jedi]

        # the rest are immutable anyway
        new_state.maxs_turn = self.maxs_turn
        new_state.cachedTerminal = self.cachedTerminal
        new_state.cachedOutcome = self.cachedOutcome
        new_state.stringified = self.stringified
        new_state.moves_made = self.moves_made

        return new_state

    def display(self):
        """
        Present the game state to the console.
        """
        for r in range(self.dim):
            rr = self.dim - r - 1
            for c in range(self.dim):
                if (rr, c) in self.sith:
                    print('S', end='')
                elif (rr, c) in self.rebels:
                    print('R', end='')
                elif (rr, c) in self.jedi:
                    print('J', end='')
                else:
                    print('.', end='')
            print()

    def __str__(self):
        """ Translate the board description into a string.  
            Could be used as a key for a hash table.  
            :return: A string that describes the board in the current state.
        """
        s = ""
        for r in range(self.dim):
            for c in range(self.dim):
                if (r, c) in self.sith:
                    s += 'S'
                elif (r, c) in self.rebels:
                    s += 'R'
                elif (r, c) in self.jedi:
                    s += 'J'
                else:
                    s += ' '
        return s

    def _occupied(self, r, c):
        """ Determine if the given location is occupied by one of the pieces.
            :param: r,c: integers
            :return: True if (r,c) is one of the pieces still on the board
        """
        return (r, c) in self.rebels or (r, c) in self.jedi or (r, c) in self.sith


class Game(object):
    """ The Game object defines the interface that is used by Game Tree Search
        implementation.
    """

    def __init__(self, dim=5, depthlimit=0, movelimit=40):
        """ Initialization.  
        """
        self.dim = dim
        self.depth_limit = depthlimit
        self.move_limit = movelimit

    def initial_state(self):
        """ Return an initial state for the game.
        """
        # the default GameState constructor creates the initial starting position
        state = GameState(dim=self.dim)
        state.sith.append((self.dim-1, self.dim//2))
        for c in range(0, self.dim, 1):
            state.rebels.append((0, c))
        state.stringified = str(state)

        return state

    def is_mins_turn(self, state):
        """ Indicate if it's Min's turn
            :return: True if it's Min's turn to play
        """
        return not state.maxs_turn

    def is_maxs_turn(self, state):
        """ Indicate if it's Min's turn
            :return: True if it's Max's turn to play
        """
        return state.maxs_turn

    def is_terminal(self, state):
        """ Indicate if the game is over.
            :param node: a game state with stored game state
            :return: a boolean indicating if node is terminal
        """
        return state.cachedTerminal or state.moves_made > self.move_limit

    def actions(self, state):
        """ Returns all the legal actions in the given state.
            :param state: a state object
            :return: a list of actions legal in the given state
        """
        if state.maxs_turn:
            # broken into 2 private methods
            some = self.__rebel_actions(state) + self.__jedi_actions(state)
            if len(some) == 0:
                return [None]
            else:
                return some
        else:
            return self.__sith_actions(state)

    def result(self, state, action):
        """ Return the state that results from the application of the
            given action in the given state.
            :param state: a legal game state
            :param action: a legal action in the game state
            :return: a new game state
        """

        # first make a copy of the state
        new_state = state.myclone()
        new_state.moves_made += 1

        if action is None:
            new_state.cachedTerminal = True
            new_state.cachedOutcome = None
            return new_state

        # my actions are 4-tuples, with the old and new positions
        oldr, oldc, newr, newc = action

        if state.maxs_turn:
            self.__player1_result(state, new_state, action)
        else:
            self.__player2_result(state, new_state, action)

        new_state.maxs_turn = not state.maxs_turn

       # check if the move was a winning move here
        self._cache_outcome(new_state)

        # now, finally, create the stringification
        new_state.stringified = str(new_state)

        return new_state

    def utility(self, state):
        """ Calculate the utility of the given state.
            :param state: a legal game state
            :return: utility of the terminal state
        """
        if state.cachedTerminal and state.cachedOutcome is None:
            return 0
        if state.cachedTerminal and state.cachedOutcome:
            return 100
        elif state.cachedTerminal and not state.cachedOutcome:
            return -100
        else:
            return 0

    def cutoff_test(self, state, depth):
        """
            Check if the search should be cut-off early.
            In a more interesting game, you might look at the state
            and allow a deeper search in important branches, and a shallower
            search in boring branches.

            :param state: a game state
            :param depth: the depth of the state,
                          in terms of levels below the start of search.
            :return: True if search should be cut off here.
        """
        return depth > self.depth_limit

    def eval(self, state):
        """
            When a depth limit is applied, we need to evaluate the
            given state to estimate who might win.
            state: a legal game state
            :return: a numeric value in the range of the utility function
        """
        return 2*len(state.rebels) + 10*len(state.jedi) - 5*len(state.sith)

    def congratulate(self, state):
        """ Called at the end of a game, display some appropriate 
            sentiments to the console. Could be used to display 
            game statistics as well.
            :param state: a legal game state
        """
        winstring = '{} wins (utility: {}, moves: {})'
        if state.cachedOutcome is None:
            print('Draw')
        elif state.cachedOutcome:
            print(winstring.format('Player 1',
                  self.utility(state), state.moves_made))
        else:
            print(winstring.format('Player 2',
                  self.utility(state), state.moves_made))

        return  # not really needed, but indicates the end of the method

    def transposition_string(self, state):
        """ Returns a unique string for the given state.  For use in 
            any Game Tree Search that employs a transposition table.
            :param state: a legal game state
            :return: a unique string representing the state
        """
        return state.stringified

    # all remaining methods are to assist in the calculations

    def _inbounds(self, r, c):
        """ Determine if the given location is a legal position on the board.
            :param: r,c: integers
            :return: True if (r,c) is on the board
        """
        return 0 <= r < self.dim and 0 <= c < self.dim

    def __sith_actions(self, state):
        """ Returns a list of moves for the Sith pieces.
            The Sith moves like a King in Chess
            :param state: a legal game state
            :return: a list of sith actions in the given state
        """
        all_moves = []
        for sr, sc in state.sith:
            # eight possible movements
            for (i, j) in [(1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1)]:
                # check if in bounds
                if self._inbounds(sr+i, sc+j) and (sr+i, sc+j) not in state.sith:
                    all_moves.append((sr, sc, sr+i, sc+j))

        return all_moves

    def __rebel_actions(self, state):
        """ Returns a list of moves for the Rebel pieces.
            The Rebel moves like a Pawn in Chess.
            In this version, Rebels cannot capture!

            :param state: a legal game state
            :return: a list of rebel actions in the given state
        """
        all_moves = []
        for rr, rc in state.rebels:
            if self._inbounds(rr+1, rc) and not state._occupied(rr+1, rc):
                all_moves.append((rr, rc, rr+1, rc))

        return all_moves

    def __jedi_actions(self, state):
        """ Returns a list of moves for the Sith pieces.
            The Sith moves like a Queen in Chess.
            :param state: a legal game state
            :return: a list of jedi actions in the given state
        """
        all_moves = []
        for jr, jc in state.jedi:
            # 8 directions
            for (dr, dc) in [(1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1)]:
                i = 1
                # walk along the (dr,dc) direction until the edge or an occupied square
                while self._inbounds(jr+i*dr, jc+i*dc) and not state._occupied(jr+i*dr, jc+i*dc):
                    all_moves.append((jr, jc, jr+i*dr, jc+i*dc))
                    i += 1
                # but if the occupied square is Sith, add the capture move
                if (jr+i*dr, jc+i*dc) in state.sith:
                    all_moves.append((jr, jc, jr+i*dr, jc+i*dc))

        return all_moves

    def __player1_result(self, state, new_state, action):
        """ process the results of the action in the newstate 
            assuming the action is player 1 (the rebels and jedi)
            This method mutates newstate.

            :param state: a legal game state
            :param new_state: a clone of state, to be mutated
            :param action: a legal action in the game state
            Return: None (newstate is modified)
        """
        oldr, oldc, newr, newc = action

        # Player 1 moved
        if (newr, newc) in new_state.sith:
            # and captured a Sith!
            new_state.sith.remove((newr, newc))

        if (oldr, oldc) in state.rebels:
            # it was a rebel that moved
            new_state.rebels.remove((oldr, oldc))
            if newr == self.dim - 1:
                # promotion to Jedi
                new_state.jedi.append((newr, newc))
            else:
                new_state.rebels.append((newr, newc))
        else:
            # it was a jedi that moved
            new_state.jedi.remove((oldr, oldc))
            new_state.jedi.append((newr, newc))

    def __player2_result(self, state, new_state, action):
        """ process the results of the action in the newstate 
            assuming the action is player 1 (the sith)
            This method mutates newstate.

            :param state: a legal game state
            :param new_state: a clone of state, to be mutated
            :param action: a legal action in the game state
            Return: None (newstate is modified)
        """
        oldr, oldc, newr, newc = action

        # Player 2 moved
        if (newr, newc) in state.rebels:
            # captured a Rebel
            new_state.rebels.remove((newr, newc))
            # move the Sith
            new_state.sith.remove((oldr, oldc))
            new_state.sith.append((newr, newc))
        elif (newr, newc) in state.jedi:
            # converted a Jedi
            new_state.jedi.remove((newr, newc))
            new_state.sith.append((newr, newc))
        else:
            # Sith movement only
            new_state.sith.remove((oldr, oldc))
            new_state.sith.append((newr, newc))

    def _cache_outcome(self, state):
        """ Look at the board and check if the new move was a winner.
            :param state: a legal game state
            :return:
        """
        if len(state.sith) == 0:
            state.cachedTerminal = True
            state.cachedOutcome = True  # Max
        elif len(state.rebels) == 0 and len(state.jedi) == 0:
            state.cachedTerminal = True
            state.cachedOutcome = False  # Min
        else:
            state.cachedTerminal = False
            state.cachedOutcome = None

# eof
