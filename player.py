"""CSC148 Assignment 2

=== CSC148 Winter 2020 ===
Department of Computer Science,
University of Toronto

This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

Authors: Diane Horton, David Liu, Mario Badr, Sophia Huynh, Misha Schwartz,
and Jaisie Sin

All of the files in this directory and all subdirectories are:
Copyright (c) Diane Horton, David Liu, Mario Badr, Sophia Huynh,
Misha Schwartz, and Jaisie Sin.

=== Module Description ===

This file contains the hierarchy of player classes.
"""
from __future__ import annotations
from typing import List, Optional, Tuple
import random
import pygame

from block import Block
from goal import Goal, generate_goals

from actions import KEY_ACTION, ROTATE_CLOCKWISE, ROTATE_COUNTER_CLOCKWISE, \
    SWAP_HORIZONTAL, SWAP_VERTICAL, SMASH, PASS, PAINT, COMBINE


def create_players(num_human: int, num_random: int, smart_players: List[int]) \
        -> List[Player]:
    """Return a new list of Player objects.

    <num_human> is the number of human player, <num_random> is the number of
    random players, and <smart_players> is a list of difficulty levels for each
    SmartPlayer that is to be created.

    The list should contain <num_human> HumanPlayer objects first, then
    <num_random> RandomPlayer objects, then the same number of SmartPlayer
    objects as the length of <smart_players>. The difficulty levels in
    <smart_players> should be applied to each SmartPlayer object, in order.
    """
    players = []
    goals = generate_goals(num_human + num_random + len(smart_players))

    for i in range(num_human):
        players.append(HumanPlayer(i, goals[i]))

    for j in range(num_human, num_random + num_human):
        players.append(RandomPlayer(j, goals[j]))

    count = num_random + num_human
    for diff in smart_players:
        players.append(SmartPlayer(count, goals[count], diff))
        count += 1

    return players


def _get_block(block: Block, location: Tuple[int, int], level: int) -> \
        Optional[Block]:
    """Return the Block within <block> that is at <level> and includes
    <location>. <location> is a coordinate-pair (x, y).

    A block includes all locations that are strictly inside of it, as well as
    locations on the top and left edges. A block does not include locations that
    are on the bottom or right edge.

    If a Block includes <location>, then so do its ancestors. <level> specifies
    which of these blocks to return. If <level> is greater than the level of
    the deepest block that includes <location>, then return that deepest block.

    If no Block can be found at <location>, return None.

    Preconditions:
        - 0 <= level <= max_depth
    """
    # Check if it's the deepest block or if it is the block that is wanted
    if not block.children or level == 0 and 0 <= location[0] and 0 <= \
            location[1]:
        return block
    # recurse through the children
    else:
        section = block.size // 2
        # check if it within the left half of pixels
        if 0 <= block.position[0] <= location[0] < block.position[0] + section:
            if 0 <= block.position[1] <= location[1] < block.position[1] + \
                    section:
                return _get_block(block.children[1], location, level - 1)
            else:
                return _get_block(block.children[2], location, level - 1)
        # otherwise check if it is within the right half of pixels
        elif 0 <= block.position[0] + section <= location[0] < block.size + \
                block.position[0]:
            if 0 <= block.position[1] <= location[1] < block.position[1] + \
                    section:
                return _get_block(block.children[0], location, level - 1)
            elif block.position[1] + section <= location[1] < block.size + \
                    block.position[1]:
                return _get_block(block.children[3], location, level - 1)
        return None


class Player:
    """A player in the Blocky game.

    This is an abstract class. Only child classes should be instantiated.

    === Public Attributes ===
    id:
        This player's number.
    goal:
        This player's assigned goal for the game.
    """
    id: int
    goal: Goal

    def __init__(self, player_id: int, goal: Goal) -> None:
        """Initialize this Player.
        """
        self.goal = goal
        self.id = player_id

    def get_selected_block(self, board: Block) -> Optional[Block]:
        """Return the block that is currently selected by the player.

        If no block is selected by the player, return None.
        """
        raise NotImplementedError

    def process_event(self, event: pygame.event.Event) -> None:
        """Update this player based on the pygame event.
        """
        raise NotImplementedError

    def generate_move(self, board: Block) -> \
            Optional[Tuple[str, Optional[int], Block]]:
        """Return a potential move to make on the game board.

        The move is a tuple consisting of a string, an optional integer, and
        a block. The string indicates the move being made (i.e., rotate, swap,
        or smash). The integer indicates the direction (i.e., for rotate and
        swap). And the block indicates which block is being acted on.

        Return None if no move can be made, yet.
        """
        raise NotImplementedError


def _create_move(action: Tuple[str, Optional[int]], block: Block) -> \
        Tuple[str, Optional[int], Block]:
    return action[0], action[1], block


class HumanPlayer(Player):
    """A human player.
    """
    # === Private Attributes ===
    # _level:
    #     The level of the Block that the user selected most recently.
    # _desired_action:
    #     The most recent action that the user is attempting to do.
    #
    # == Representation Invariants concerning the private attributes ==
    #     _level >= 0
    _level: int
    _desired_action: Optional[Tuple[str, Optional[int]]]

    def __init__(self, player_id: int, goal: Goal) -> None:
        """Initialize this HumanPlayer with the given <renderer>, <player_id>
        and <goal>.
        """
        Player.__init__(self, player_id, goal)

        # This HumanPlayer has not yet selected a block, so set _level to 0
        # and _selected_block to None.
        self._level = 0
        self._desired_action = None

    def get_selected_block(self, board: Block) -> Optional[Block]:
        """Return the block that is currently selected by the player based on
        the position of the mouse on the screen and the player's desired level.

        If no block is selected by the player, return None.
        """
        mouse_pos = pygame.mouse.get_pos()
        block = _get_block(board, mouse_pos, self._level)

        return block

    def process_event(self, event: pygame.event.Event) -> None:
        """Respond to the relevant keyboard events made by the player based on
        the mapping in KEY_ACTION, as well as the W and S keys for changing
        the level.
        """
        if event.type == pygame.KEYDOWN:
            if event.key in KEY_ACTION:
                self._desired_action = KEY_ACTION[event.key]
            elif event.key == pygame.K_w:
                self._level = max(0, self._level - 1)
                self._desired_action = None
            elif event.key == pygame.K_s:
                self._level += 1
                self._desired_action = None

    def generate_move(self, board: Block) -> \
            Optional[Tuple[str, Optional[int], Block]]:
        """Return the move that the player would like to perform. The move may
        not be valid.

        Return None if the player is not currently selecting a block.
        """
        block = self.get_selected_block(board)

        if block is None or self._desired_action is None:
            return None
        else:
            move = _create_move(self._desired_action, block)

            self._desired_action = None
            return move


class RandomPlayer(Player):
    """
    A random action player
    """
    # === Private Attributes ===
    # _proceed:
    #   True when the player should make a move, False when the player should
    #   wait.
    _proceed: bool

    def __init__(self, player_id: int, goal: Goal) -> None:
        Player.__init__(self, player_id, goal)
        self._proceed = False

    def get_selected_block(self, board: Block) -> Optional[Block]:
        return None

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._proceed = True

    def generate_move(self, board: Block) ->\
            Optional[Tuple[str, Optional[int], Block]]:
        """Return a valid, randomly generated move.

        A valid move is a move other than PASS that can be successfully
        performed on the <board>.

        This function does not mutate <board>.
        """
        if not self._proceed:
            return None  # Do not remove

        board_copy = board.create_copy()
        rand_x = random.randint(0, board_copy.size)
        rand_y = random.randint(0, board_copy.size)
        rand_level = random.randint(0, board.max_depth)

        rand_block = _get_block(board_copy, (rand_x, rand_y), rand_level)

        # this is to in case rand_block is None
        # location does not include the bottom or right edge
        # so sometimes _get_block returns None
        while rand_block is None:
            rand_x = random.randint(0, board.size)
            rand_y = random.randint(0, board.size)
            rand_level = random.randint(0, board.max_depth)
            rand_block = _get_block(board_copy,
                                    (rand_x, rand_y),
                                    rand_level)

        # Generate a random number to then choose a move
        moves = ['smash', 'swap_hori', 'swap_vert', 'rotate_clock',
                 'rotate_counter', 'paint', 'combine']
        move = None
        actual_block = _get_block(board, (rand_x, rand_y), rand_level)
        # Checks if the random action chosen by a random number in the range of
        # the length of list <moves> is a valid action.
        # if it isn't valid, removes that move from the list and tries again
        # if it reaches a point when <moves> is empty, the loop exits, and
        # returns pass as the valid move
        while move is None and moves:
            num = random.randint(0, len(moves) - 1)
            if moves[num] == 'smash':
                if rand_block.smashable():
                    move = _create_move(SMASH, actual_block)
                else:
                    moves.remove('smash')
            elif moves[num] == 'swap_hori':
                if rand_block.swap(0):
                    move = _create_move(SWAP_HORIZONTAL, actual_block)
                else:
                    moves.remove('swap_hori')
            elif moves[num] == 'swap_vert':
                if rand_block.swap(1):
                    move = _create_move(SWAP_VERTICAL, actual_block)
                else:
                    moves.remove('swap_vert')
            elif moves[num] == 'rotate_clock':
                if rand_block.rotate(1):
                    move = _create_move(ROTATE_CLOCKWISE, actual_block)
                else:
                    moves.remove('rotate_clock')
            elif moves[num] == 'rotate_counter':
                if rand_block.rotate(3):
                    move = _create_move(ROTATE_COUNTER_CLOCKWISE, actual_block)
                else:
                    moves.remove('rotate_counter')
            elif moves[num] == 'paint':
                if rand_block.paint(self.goal.colour):
                    move = _create_move(PAINT, actual_block)
                else:
                    moves.remove('paint')
            else:
                if rand_block.combine():
                    move = _create_move(COMBINE, actual_block)

        if not moves:
            move = _create_move(PASS, actual_block)

        self._proceed = False  # Must set to False before returning!
        return move


class SmartPlayer(Player):
    """ a Player that picks the best move out of
    self._difficulty number of random moves

    === Private Attributes ===
    _proceed:
      True when the player should make a move, False when the player should
      wait.
    _difficulty: int representing the how how difficult it is
      to play against this player
    """
    _proceed: bool
    _difficulty: int

    def __init__(self, player_id: int, goal: Goal, difficulty: int) -> None:

        Player.__init__(self, player_id, goal)
        self._difficulty = difficulty
        self._proceed = False

    def get_selected_block(self, board: Block) -> Optional[Block]:
        return None

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._proceed = True

    def generate_move(self, board: Block) ->\
            Optional[Tuple[str, Optional[int], Block]]:
        """Return a valid move by assessing multiple valid moves and choosing
        the move that results in the highest score for this player's goal (i.e.,
        disregarding penalties).

        A valid move is a move other than PASS that can be successfully
        performed on the <board>. If no move can be found that is better than
        the current score, this player will pass.

        This function does not mutate <board>.
        """

        if not self._proceed:
            return None  # Do not remove

        # assume that current score is best possible score
        best_score = self.goal.score(board)
        action = "pass"   # string representation of move
        direction = None  # int for direction for rotate or swap
        block_copy = None  # the block being operated on in the copy of board

        # generating self._difficulty number of random valid moves
        num_moves = self._difficulty
        for _ in range(num_moves):
            # find random move
            new_action, new_direction, rand_block, new_score \
                = self._generate_random_move(board)

            # find score for this random move
            # disregard any penalties
            if new_score > best_score:
                best_score = new_score
                block_copy = rand_block
                action = new_action
                direction = new_direction

        # TEST
        # print("action:" + action)
        # print("direction: " + str(direction))

        # finding the parallel block on board as block on board_copy
        block = board
        if action != "pass":
            block = _get_block(board, block_copy.position, block_copy.level)

        self._proceed = False  # Must set to False before returning!

        return action, direction, block

    def _generate_random_move(self, board: Block) ->\
            Tuple[str, int, Block, int]:
        """return a 4 element Tuple that represents a move and score
        (action, direction, block(on copy of board), score)
        board is NOT mutated
        """
        is_valid_move = False

        # for pyTA
        board_copy = None
        new_action = None
        new_direction = None
        rand_block = None

        while not is_valid_move:
            # defining this variable since it's not always defined below
            new_direction = None

            # copy of board
            board_copy = board.create_copy()

            # find random action, there are 7 possible actions
            rand_action = random.randint(0, 6)

            # find random block
            rand_x = random.randint(0, board.size)
            rand_y = random.randint(0, board.size)
            rand_level = random.randint(0, board.max_depth)
            rand_block = _get_block(board_copy,
                                    (rand_x, rand_y),
                                    rand_level)

            # this is to in case rand_block is None
            # location does not include the bottom or right edge
            # so sometimes _get_block returns None
            while rand_block is None:
                rand_x = random.randint(0, board.size)
                rand_y = random.randint(0, board.size)
                rand_level = random.randint(0, board.max_depth)
                rand_block = _get_block(board_copy,
                                        (rand_x, rand_y),
                                        rand_level)

            if rand_action == 0:
                # Note: although smash won't guarantee the same score
                # still treat it like other actions -> piazza @1719
                new_action = 'smash'
                if rand_block.smash():
                    # if move is valid
                    is_valid_move = True

            elif rand_action == 1:
                new_action = 'swap'
                new_direction = 0  # horizontal swap
                if rand_block.swap(0):
                    # if move is valid
                    is_valid_move = True

            elif rand_action == 2:
                new_action = 'swap'
                new_direction = 1  # vertical swap
                if rand_block.swap(1):
                    # if move is valid
                    is_valid_move = True

            elif rand_action == 3:
                new_action = 'rotate'
                new_direction = 1  # clockwise rotation
                if rand_block.rotate(1):
                    # if move is valid
                    is_valid_move = True

            elif rand_action == 4:
                new_action = 'rotate'
                new_direction = 3  # counter-clockwise rotation
                if rand_block.rotate(3):
                    # if move is valid
                    is_valid_move = True

            elif rand_action == 5:
                new_action = 'paint'
                if rand_block.paint(self.goal.colour):
                    # if move is valid
                    is_valid_move = True

            elif rand_action == 6:
                new_action = 'combine'
                if rand_block.combine():
                    # if move is valid
                    is_valid_move = True

        return new_action, new_direction,\
               rand_block, self.goal.score(board_copy)

if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-io': ['process_event'],
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing', 'actions', 'block',
            'goal', 'pygame', '__future__'
        ],
        'max-attributes': 10,
        'generated-members': 'pygame.*'
    })
