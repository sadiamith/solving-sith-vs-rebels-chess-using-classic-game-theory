##########################################################################################
class PlayerInterface(object):
    """ A base class for Player interfaces
        Just remember what game is being played.
    """

    def __init__(self, game):
        self.game = game


##########################################################################################
class HumanMenu(PlayerInterface):
    """ This interface puts the actions in a menu, asks for a choice
        from the menu, and waits for the user to type something.
    """

    def __init__(self, game):
        PlayerInterface.__init__(self, game)

    def ask_move(self, state):
        """ Present the human player with a menu of possible moves.
            The moves are obtained from the game, so they should be legal.
            :param state: a legal game state
            :return: an action in the game
        """

        # present the user with moves that are legal
        actions = self.game.actions(state)

        print("It's the Human's turn!  Choose one of the moves:")
        for i, act in enumerate(actions):
            print("#{}: {}".format(i, self.game.action_to_string(act)))

        # wait for a valid choice from the menu
        choice = -1
        while choice > i or choice < 0:
            choice = int(input("Type in the move number: "))
            if choice > i or choice < 0:
                print("Can't choose that.")

        # return the choice
        return actions[(choice)]


##########################################################################################
class ComputerInterface(PlayerInterface):
    """ This subclass of PlayerInterface stores a search class object.
        The searcher has to have the following methods:
            minimax_decision_max(state)
            minimax_decision_min(state)
    """

    def __init__(self, game, searcher):
        PlayerInterface.__init__(self, game)
        self.searcher = searcher

    def _ask_move_searcher(self, state):
        """ This method interacts with the searcher object.
            Sub-classes can use this, and do other things as well.
            :param state: a legal game state
            :return: a SearchTerminationRecord
        """
        if self.game.is_maxs_turn(state):
            result = self.searcher.minimax_decision_max(state)
        else:
            result = self.searcher.minimax_decision_min(state)
        return result


##########################################################################################
class SilentComputer(ComputerInterface):
    """ This class has no console IO.
        The searcher has to have the following methods:
            minimax_decision_max(state)
            minimax_decision_min(state)
    """

    def __init__(self, game, searcher):
        ComputerInterface.__init__(self, game, searcher)

    def ask_move(self, state):
        """ Get a move from the search algorithm.  No console IO.
            :param state: a legal game state
            :return: a legal move in the given state as defined by game.actions()
        """
        # need to call search and return the choice
        result = super()._ask_move_searcher(state)
        return result.move


##########################################################################################
class VerboseComputer(ComputerInterface):
    """ This interface uses the ComputerInterface to get a move 
        from the searcher.
        This version has some dialogue, and shows the details about the move.  
        A bit boring?
    """

    def __init__(self, game, searcher):
        ComputerInterface.__init__(self, game, searcher)

    def ask_move(self, state):
        """ Get a move from the search algorithm.  Some dialogue on console IO.
            :param state: a legal game state
            :return: a legal move in the given state as defined by game.actions()
        """
        print("Thinking...")

        # need to call search and return the choice
        result = super()._ask_move_searcher(state)

        print("...done")
        result.display()

        return result.move
