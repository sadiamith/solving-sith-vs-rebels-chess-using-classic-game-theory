import time as time

##########################################################################################


class SearchTerminationRecord(object):
    """A record to return information about how the search turned out.
       All the details are provided in a record, to avoid needing to print out the details
       at different parts of the code.
    """

    def __init__(self, value, move, time=0, nodes=0, cutoff=False):
        self.value = value      # numeric: the minimax value
        self.move = move        # a move with the stated minimax value
        # float: how much time was spent searching?  Not really accurate, but good enough for fun
        self.time = time
        self.nodes = nodes      # integer: How many nodes were expanded during the search?
        self.cutoff = cutoff    # boolean: was the search cut-off?

    def __str__(self):
        """Create a string representation of the Result data
           This string doesn't show everything it could.
        """
        text = 'Chose move <{}> with {} Minimax value {} after {:.4f} seconds, expanding {} nodes'
        # if self.cutoff:
        # textsuccess = 'estimated'
        # else:
        # textsuccess = 'true'
        # cutoff reporting not implemented
        textsuccess = ""
        return text.format(self.move, textsuccess, self.value, self.time, self.nodes)

    def display(self):
        """Display the record to the console
        """
        print(str(self))


##########################################################################################
class Minimax(object):
    """ An implementation of MiniMax Search
        - with data tracked for runtime or search effort
        - with search cut-off
        - no transposition table
    """

    # a clumsy way to represent a large value
    ifny = 2**20

    def __init__(self, game):
        """ Remember the game object.
            :param: game: an object from the Game Class, with methods as described
                    at the top of this document.
        """
        self.game = game
        self.nodes_expanded = 0
        self.transposition_table = None

    def minimax_decision_max(self, state):
        """ Return the move that Max should take in the given state
            :param state: a legal game state
            :return: a SearchTerminationRecord
        """
        start = time.perf_counter()
        self.nodes_expanded = 0
        self.transposition_table = dict()

        # alpha beta parameters initialized here
        alpha = -self.ifny
        beta = self.ifny

        # look for the best among Max's options
        best = -self.ifny
        best_action = None

        self.nodes_expanded += 1
        for act in self.game.actions(state):
            val = self.__min_value(
                self.game.result(state, act), alpha, beta, 1)
            if val > best:
                # remember something better
                best = val
                best_action = act
            alpha = max(alpha, best)

        end = time.perf_counter()

        return SearchTerminationRecord(best, best_action, end - start, self.nodes_expanded)

    def minimax_decision_min(self, state):
        """ Return the move that Min should take in the given state
            :param state: a legal game state
            :return: a SearchTerminationRecord
        """
        start = time.perf_counter()
        self.nodes_expanded = 0
        self.transposition_table = dict()

        # alpha beta parameters initialized here
        alpha = -self.ifny
        beta = self.ifny

        # look for the best among Min's options
        best = self.ifny
        best_action = None

        self.nodes_expanded += 1
        for act in self.game.actions(state):
            val = self.__max_value(
                self.game.result(state, act), alpha, beta, 1)
            if val < best:
                # remember something better
                best = val
                best_action = act
            beta = min(beta, best)

        end = time.perf_counter()

        return SearchTerminationRecord(best, best_action, end - start, self.nodes_expanded)

    def __max_value(self, state, alpha, beta, depth):
        """ Return the minimax value of the given state, assuming Max's turn to move.
            :param state: a legal game state
            :param alpha: the best max can do elsewhere
            :param beta: the best Min can do elsewhere
            :param depth: an integer representing the depth of the state
            :return: the value that Max can obtain here
        """
        state_string = self.game.transposition_string(state)
        if state_string in self.transposition_table:
            best = self.transposition_table[state_string]
        elif self.game.is_terminal(state):
            # the game is over, return the utility
            best = self.game.utility(state)
        elif self.game.cutoff_test(state, depth):
            best = self.game.eval(state)
        else:
            # look for the best among Max's options
            best = -self.ifny
            self.nodes_expanded += 1
            for act in self.game.actions(state):
                val = self.__min_value(self.game.result(
                    state, act), alpha, beta, depth+1)
                if val > best:
                    # remember something better
                    best = val
                if best >= beta:
                    return best
                alpha = max(alpha, best)
            self.transposition_table[state_string] = best
        return best

    def __min_value(self, state, alpha, beta, depth):
        """ Return the minimax value of the given state, assuming Min's turn to move.
            :param state: a legal game state
            :param alpha: the best max can do elsewhere
            :param beta: the best Min can do elsewhere
            :param depth: an integer representing the depth of the state
            :return: the value that Min can obtain here
        """
        state_string = self.game.transposition_string(state)
        if state_string in self.transposition_table:
            best = self.transposition_table[state_string]
        elif self.game.is_terminal(state):
            # the game is over, return the utility
            best = self.game.utility(state)
        elif self.game.cutoff_test(state, depth):
            best = self.game.eval(state)
        else:
            # look for the best among Max's options
            best = self.ifny
            self.nodes_expanded += 1
            for act in self.game.actions(state):
                val = self.__max_value(self.game.result(
                    state, act), alpha, beta, depth+1)
                if val < best:
                    # remember something better
                    best = val
                if best <= alpha:
                    return best
                beta = min(beta, best)
            self.transposition_table[state_string] = best
        return best
