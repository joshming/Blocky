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
Misha Schwartz, and Jaisie Sin

=== Module Description ===

This file contains the hierarchy of Goal classes.
"""
from __future__ import annotations
import random
from typing import List, Tuple
from block import Block
from settings import colour_name, COLOUR_LIST


def generate_goals(num_goals: int) -> List[Goal]:
    """Return a randomly generated list of goals with length num_goals.

    All elements of the list must be the same type of goal, but each goal
    must have a different randomly generated colour from COLOUR_LIST. No two
    goals can have the same colour.

    Precondition:
        - num_goals <= len(COLOUR_LIST)
    """
    goals = []
    # copy of colour list
    colour_copy = COLOUR_LIST[:]

    # random goal type
    goal_type = random.randint(0, 5)

    # Perimeter goal
    if goal_type % 2 == 0:
        while len(goals) < num_goals:
            # random colour
            type_colour = random.randint(0, len(colour_copy)-1)

            new_goal = PerimeterGoal(colour_copy[type_colour])
            goals.append(new_goal)

            # popping colour from colour list so it doesn't get chosen again
            colour_copy.pop(type_colour)
    # Blob goal
    else:
        while len(goals) < num_goals:
            # random colour
            type_colour = random.randint(0, len(colour_copy)-1)

            new_goal = BlobGoal(colour_copy[type_colour])
            goals.append(new_goal)

            # popping colour from colour list so it doesn't get chosen again
            colour_copy.pop(type_colour)

    return goals


def _flatten(block: Block) -> List[List[Tuple[int, int, int]]]:
    """Return a two-dimensional list representing <block> as rows and columns of
    unit cells.

    Return a list of lists L, where,
    for 0 <= i, j < 2^{max_depth - self.level}
        - L[i] represents column i and
        - L[i][j] represents the unit cell at column i and row j.

    Each unit cell is represented by a tuple of 3 ints, which is the colour
    of the block at the cell location[i][j]

    L[0][0] represents the unit cell in the upper left corner of the Block.
    """
    # size of unit cell
    unit_size = 2 ** block.max_depth // 2 ** block.level
    # if block does not have children (block.children == [])
    lst = []
    if block.colour is not None and not block.children:
        # populating lst with unit cells with only block.colour
        for i in range(unit_size):
            # adding empty column
            lst.append([])
            for _ in range(unit_size):
                # populating that column with unit_size items
                lst[i].append(block.colour)

    else:  # block has children

        # flattening each child first
        lst0 = _flatten(block.children[0])  # upper right
        lst1 = _flatten(block.children[1])  # upper left
        lst2 = _flatten(block.children[2])  # lower left
        lst3 = _flatten(block.children[3])  # lower right

        # combining the sublists of each child
        # left blocks
        for i in range(len(lst1)):
            # adding the columns together
            # upper left then lower left
            lst.append(lst1[i] + lst2[i])
        # right blocks
        for i in range(len(lst0)):
            # adding the rows together
            # upper right then lower right
            lst.append(lst0[i] + lst3[i])

    return lst


class Goal:
    """A player goal in the game of Blocky.

    This is an abstract class. Only child classes should be instantiated.

    === Attributes ===
    colour:
        The target colour for this goal, that is the colour to which
        this goal applies.
    """
    colour: Tuple[int, int, int]

    def __init__(self, target_colour: Tuple[int, int, int]) -> None:
        """Initialize this goal to have the given target colour.
        """
        self.colour = target_colour

    def score(self, board: Block) -> int:
        """Return the current score for this goal on the given board.

        The score is always greater than or equal to 0.
        """
        raise NotImplementedError

    def description(self) -> str:
        """Return a description of this goal.
        """
        raise NotImplementedError


class PerimeterGoal(Goal):
    """ A player goal in the game of Blocky, a child of the Goal class

    This The player must put the most possible units of the goal colour
    on the outer perimeter of the board. The player's score is the total
    unit cells of the goal colour. Corner cells are worth double points.

    === Attributes ===
    colour:
        The target colour for this goal, that is the colour to which
        this goal applies.
    """
    colour: Tuple[int, int, int]

    def score(self, board: Block) -> int:
        flat_board = _flatten(board)
        top_bot_score = 0
        for inner in flat_board:
            # adds the score for the top edge, since only the first index in
            # each column is at the top of a block
            if inner[0] == self.colour:
                top_bot_score += 1
            # does the same for the bottom
            if inner[-1] == self.colour:
                top_bot_score += 1

        side_score = 0
        for i in range(len(flat_board[0])):
            # Only first and last sublist can add to the score, so just check
            # those
            if flat_board[0][i] == self.colour:
                side_score += 1
            if flat_board[-1][i] == self.colour:
                side_score += 1

        return side_score + top_bot_score

    def description(self) -> str:
        # creating string representation of colour
        # using colour name function in settings
        str_colour = colour_name(self.colour)
        return f"Put the most possible units of {str_colour}" \
               f"on the outer perimeter of the board. Corners are worth double."


class BlobGoal(Goal):
    """ A player goal in the game of Blocky, a child of the Goal class

    The player must create the larger 'blob' of the goal colour.
    A blob is a group of connected blocks with the same colour.
    Blocks are connected only if their sides touch.
    The score is the number of unit cells in the largest blob.

    === Attributes ===
    colour:
        The target colour for this goal, that is the colour to which
        this goal applies.
    """
    colour: Tuple[int, int, int]

    def score(self, board: Block) -> int:
        # flattened board
        flat_board = _flatten(board)

        # making the visited board populated with -1
        visited = []
        for i in range(len(flat_board)):
            visited.append([])
            for _ in range(len(flat_board)):
                visited[i].append(-1)

        # looking for largest blob
        largest_blob = 0
        for column in range(len(flat_board)):
            for row in range(len(flat_board)):
                new_blob = self._undiscovered_blob_size((column, row),
                                                        flat_board, visited)
                if new_blob > largest_blob:
                    largest_blob = new_blob

        return largest_blob

    def _undiscovered_blob_size(self, pos: Tuple[int, int],
                                board: List[List[Tuple[int, int, int]]],
                                visited: List[List[int]]) -> int:
        """Return the size of the largest connected blob that (a) is of this
        Goal's target colour, (b) includes the cell at <pos>, and (c) involves
        only cells that have never been visited.

        If <pos> is out of bounds for <board>, return 0.

        <board> is the flattened board on which to search for the blob.
        <visited> is a parallel structure that, in each cell, contains:
            -1 if this cell has never been visited
            0  if this cell has been visited and discovered
               not to be of the target colour
            1  if this cell has been visited and discovered
               to be of the target colour

        Update <visited> so that all cells that are visited are marked with
        either 0 or 1.
        """
        # pos is (column, row)
        column = pos[0]
        row = pos[1]

        # if pos is out of bounds for board
        if column >= len(board) or row >= len(board):
            return 0

        if board[column][row] != self.colour:
            # if the colour at this position is not the goal colour
            visited[column][row] = 0
            return 0
        elif visited[column][row] == 1:
            # this cell has already been counted before
            # don't count it again
            return 0

        # we now know that this cell is the goal colour
        visited[column][row] = 1

        # need to check 4 cells, above, below, right, left (of pos)
        # variables storing the cells part of the blob in each direction
        left = 0
        right = 0
        above = 0
        below = 0

        if column != 0:
            # if pos is NOT in first column we can check cell to the left
            if visited[column-1][row] == 0 or visited[column-1][row] == 1:
                # this cell has been visited before
                pass
            elif board[column-1][row] != self.colour:
                # this cell doesn't match goal colour
                visited[column-1][row] = 0
            else:
                # this cell is the goal colour
                # recursive call to find more parts of blob
                left = self._undiscovered_blob_size((column-1, row),
                                                    board, visited)

        if column != len(board) - 1:
            # if pos is NOT in last column we can check cell to the right
            if visited[column+1][row] == 0 or visited[column+1][row] == 1:
                # this cell has been visited before
                pass
            elif board[column+1][row] != self.colour:
                # this cell doesn't match goal colour
                visited[column+1][row] = 0
            else:
                # this cell is the goal colour
                # recursive call to find more parts of blob
                right = self._undiscovered_blob_size((column+1, row),
                                                     board, visited)

        if row != 0:
            # if pos is NOT in first row we can check cell above
            if visited[column][row-1] == 0 or visited[column][row-1] == 1:
                # this cell has been visited before
                pass
            elif board[column][row-1] != self.colour:
                # this cell doesn't match goal colour
                visited[column][row-1] = 0
            else:
                # this cell is the goal colour
                # recursive call to find more parts of blob
                above = self._undiscovered_blob_size((column, row-1),
                                                     board, visited)

        if row != len(board) - 1:
            # if pos is NOT in last row we can check cell below
            if visited[column][row+1] == 0 or visited[column][row+1] == 1:
                # this cell has been visited before
                pass
            elif board[column][row+1] != self.colour:
                # this cell doesn't match goal colour
                visited[column][row+1] = 0
            else:
                # this cell is the goal colour
                # recursive call to find more parts of blob
                below = self._undiscovered_blob_size((column, row+1),
                                                     board, visited)

        # cell at pos counts as 1
        return left + right + above + below + 1

    def description(self) -> str:
        # creating string representation of colour
        # using colour name function in settings
        str_colour = colour_name(self.colour)
        return f"Create the larger 'blob' of {str_colour}." \
               f"A blob is a group of connected blocks with the same colour."


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing', 'block', 'settings',
            'math', '__future__'
        ],
        'max-attributes': 15
    })
