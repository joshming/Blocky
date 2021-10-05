from typing import List, Optional, Tuple
import os
import pygame
import pytest

from block import Block
from blocky import _block_to_squares
from goal import BlobGoal, PerimeterGoal, _flatten
from player import _get_block, Player, SmartPlayer, RandomPlayer, _create_move
from renderer import Renderer
from settings import COLOUR_LIST
from actions import KEY_ACTION, ROTATE_CLOCKWISE, ROTATE_COUNTER_CLOCKWISE, \
    SWAP_HORIZONTAL, SWAP_VERTICAL, SMASH, PASS, PAINT, COMBINE


def set_children(block: Block, colours: List[Optional[Tuple[int, int, int]]]) \
        -> None:
    """Set the children at <level> for <block> using the given <colours>.

    Precondition:
        - len(colours) == 4
        - block.level + 1 <= block.max_depth
    """
    size = block._child_size()
    positions = block._children_positions()
    level = block.level + 1
    depth = block.max_depth

    block.children = []  # Potentially discard children
    for i in range(4):
        b = Block(positions[i], size, colours[i], level, depth)
        block.children.append(b)


def test_smash_on_entire_board() -> None:
    board1 = Block((0, 0), 400, COLOUR_LIST[0], 0, 0)
    assert not board1.smash()

    board2 = Block((0, 0), 400, COLOUR_LIST[0], 0, 1)
    assert board2.smash()


def test_get_block() -> None:
    board = Block((0, 0), 400, None, 0, 2)
    set_children(board, [COLOUR_LIST[0], COLOUR_LIST[1], COLOUR_LIST[2], None])
    set_children(board.children[3], [COLOUR_LIST[0], COLOUR_LIST[1], COLOUR_LIST[2], COLOUR_LIST[3]])
    actual = _get_block(board, (200, 200), 2)
    assert board.children[3].children[1] == actual


def test_get_block_2() -> None:
    board = Block((0, 0), 400, None, 0, 1)
    set_children(board, [COLOUR_LIST[0], COLOUR_LIST[1], COLOUR_LIST[2], None])
    actual = _get_block(board, (200, 200), 2)
    assert actual == board.children[3]


def test_get_block_3() -> None:
    board = Block((0, 0), 400, None, 0, 2)
    set_children(board, [COLOUR_LIST[0], COLOUR_LIST[1], COLOUR_LIST[2], None])
    set_children(board.children[3],
                 [COLOUR_LIST[0], COLOUR_LIST[1], COLOUR_LIST[2],
                  COLOUR_LIST[3]])
    actual = _get_block(board, (400, 400), 2)
    assert actual is None


def test_get_block_4() -> None:
    board = Block((0, 0), 400, None, 0, 1)
    set_children(board, [COLOUR_LIST[0], COLOUR_LIST[1], COLOUR_LIST[2], None])
    actual = _get_block(board, (500, 200), 2)
    assert actual is None


def test_get_block_5() -> None:
    board = Block((0, 0), 400, None, 0, 2)
    set_children(board, [COLOUR_LIST[0], COLOUR_LIST[1], COLOUR_LIST[2], None])
    set_children(board.children[3],
                 [COLOUR_LIST[0], COLOUR_LIST[1], COLOUR_LIST[2],
                  COLOUR_LIST[3]])
    actual = _get_block(board, (200, 500), 2)
    assert actual is None


def test_get_block_6() -> None:
    board = Block((0, 0), 400, None, 0, 2)
    set_children(board, [COLOUR_LIST[0], COLOUR_LIST[1], COLOUR_LIST[2], None])
    set_children(board.children[3],
                 [COLOUR_LIST[0], COLOUR_LIST[1], COLOUR_LIST[2],
                  COLOUR_LIST[3]])
    actual = _get_block(board, (399, 0), 2)
    assert actual == board.children[0]


def test_get_block_bot_right() -> None:
    board = Block((0, 0), 750, None, 0, 2)
    set_children(board, [COLOUR_LIST[0], COLOUR_LIST[1], COLOUR_LIST[2], None])
    set_children(board.children[3],
                 [COLOUR_LIST[0], COLOUR_LIST[1], COLOUR_LIST[2],
                  COLOUR_LIST[3]])
    actual = _get_block(board, (740, 740), 2)
    assert actual == board.children[3].children[3]


def test_get_block_top_right() -> None:
    board = Block((0, 0), 750, None, 0, 2)
    set_children(board, [None, COLOUR_LIST[0], COLOUR_LIST[1], COLOUR_LIST[2]])
    set_children(board.children[0],
                 [COLOUR_LIST[0], COLOUR_LIST[1], COLOUR_LIST[2],
                  COLOUR_LIST[3]])
    actual = _get_block(board, (749, 0), 2)
    assert actual == board.children[0].children[0]


def test_flatten_1() -> None:
    board = Block((0, 0), 750, None, 0, 3)
    set_children(board, [None, COLOUR_LIST[0], COLOUR_LIST[1], COLOUR_LIST[2]])
    set_children(board.children[0],
                 [COLOUR_LIST[0], COLOUR_LIST[1], COLOUR_LIST[2],
                  COLOUR_LIST[3]])
    actual = _flatten(board)
    expected = [[COLOUR_LIST[0], COLOUR_LIST[0], COLOUR_LIST[0], COLOUR_LIST[0],
                 COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[1]],
                [COLOUR_LIST[0], COLOUR_LIST[0], COLOUR_LIST[0], COLOUR_LIST[0],
                 COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[1]],
                [COLOUR_LIST[0], COLOUR_LIST[0], COLOUR_LIST[0], COLOUR_LIST[0],
                 COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[1],
                 COLOUR_LIST[1]],
                [COLOUR_LIST[0], COLOUR_LIST[0], COLOUR_LIST[0], COLOUR_LIST[0],
                 COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[1],
                 COLOUR_LIST[1]],
                [COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[2], COLOUR_LIST[2],
                COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[2]],
                [COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[2], COLOUR_LIST[2],
                 COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[2]],
                [COLOUR_LIST[0], COLOUR_LIST[0], COLOUR_LIST[3], COLOUR_LIST[3],
                COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[2]],
                [COLOUR_LIST[0], COLOUR_LIST[0], COLOUR_LIST[3], COLOUR_LIST[3],
                COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[2]]]
    assert actual == expected


def test_perimeter_goal_1() -> None:
    b = Block((0, 0), 400, COLOUR_LIST[0], 0, 1)
    goal = PerimeterGoal(COLOUR_LIST[0])
    actual = goal.score(b)
    assert actual == 8


def test_perimeter_goal_2() -> None:
    b = Block((0, 0), 400, COLOUR_LIST[0], 0, 0)
    goal = PerimeterGoal(COLOUR_LIST[0])
    actual = goal.score(b)
    assert actual == 4


def test_perimeter_goal_3() -> None:
    b = Block((0, 0), 400, COLOUR_LIST[0], 0, 2)
    goal = PerimeterGoal(COLOUR_LIST[0])
    actual = goal.score(b)
    assert actual == 16


def test_perimeter_goal_4() -> None:
    b = Block((0, 0), 400, COLOUR_LIST[1], 0, 1)
    goal = PerimeterGoal(COLOUR_LIST[0])
    actual = goal.score(b)
    assert actual == 0


def test_blob_goal_1() -> None:
    b = Block((0, 0), 400, COLOUR_LIST[1], 0, 0)
    goal = BlobGoal(COLOUR_LIST[1])
    actual = goal.score(b)
    assert actual == 1


def test_blob_goal_2() -> None:
    b = Block((0, 0), 400, COLOUR_LIST[1], 0, 1)
    goal = BlobGoal(COLOUR_LIST[1])
    actual = goal.score(b)
    assert actual == 4


def test_blob_goal_3() -> None:
    b = Block((0, 0), 400, COLOUR_LIST[1], 0, 2)
    goal = BlobGoal(COLOUR_LIST[1])
    actual = goal.score(b)
    assert actual == 16


def test_blob_random_player_move_1() -> None:
    b = Block((0, 0), 400, COLOUR_LIST[1], 0, 0)
    goal = BlobGoal(COLOUR_LIST[0])
    p = RandomPlayer(0, goal)
    p._proceed = True
    actual = p.generate_move(b)
    assert actual == _create_move(PAINT, b)
    assert not p._proceed


def test_blob_random_player_move_2() -> None:
    b = Block((0, 0), 400, COLOUR_LIST[1], 0, 1)
    goal = BlobGoal(COLOUR_LIST[0])
    p = RandomPlayer(0, goal)
    p._proceed = True
    actual = p.generate_move(b)
    assert actual == _create_move(SMASH, b) or actual == _create_move(PAINT, b)
    assert not p._proceed


def test_get_block_7() -> None:
    board = Block((0, 0), 400, None, 0, 2)
    set_children(board, [COLOUR_LIST[0], COLOUR_LIST[1], COLOUR_LIST[2], None])
    set_children(board.children[3],
                 [COLOUR_LIST[0], COLOUR_LIST[1], COLOUR_LIST[2],
                  COLOUR_LIST[3]])
    actual = _get_block(board, (-1, -1), 2)
    actual2 = _get_block(board, (-1, -1), 1)
    actual3 = _get_block(board, (-1, -1), 0)
    assert actual is None
    assert actual2 is None
    assert actual3 is None


if __name__ == '__main__':
    pytest.main(['A2_tests.py'])
