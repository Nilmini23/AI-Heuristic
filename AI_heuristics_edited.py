import numpy as np
import copy
import constants as c
import logic
import random
from multiprocessing.pool import ThreadPool

pool = ThreadPool(4)
transposition_table = {}

# new global setting
CURRENT_HEURISTIC = "combined"
# heuristic options -'empty_tile', 'max_tile', 'monotonocity',
# 'smoothness', 'combined'


commands = {c.KEY_UP: logic.up,
            c.KEY_DOWN: logic.down,
            c.KEY_LEFT: logic.left,
            c.KEY_RIGHT: logic.right
}


def AI_play(matrix, max_depth):
    
    # scores = pool.starmap( score_toplevel_move, [(key, matrix, max_depth) for key in commands.keys()] )

    # max_index = np.argmax(np.array(scores))
    # keys = list(commands.keys())

    # return keys[max_index]

    bestscore=-1000000
    best_key=None
  
    for key in commands.keys():
        tmp_score = score_toplevel_move(key, matrix, max_depth)
        if tmp_score>bestscore:
            bestscore = tmp_score
            best_key = key

    return best_key


def score_toplevel_move(key, board, max_depth):
    """
    Entry Point to score the first move.
    """
    newboard = commands[key](board)[0]

    if board == newboard:
        return -1000000

    # With many empty tiles calculation of many nodes would take to long and not improve the selected move
    # Less empty tiles allow for a deeper search to find a better move
    if max_depth == -1:
        empty_tiles = sum(sum(np.array(newboard)==0))

        if empty_tiles > 12:
            max_depth = 1
            
        elif empty_tiles > 7:
            max_depth = 2
            
        elif empty_tiles > 4:
            max_depth = 3
            
        elif empty_tiles >= 1:
            max_depth = 4
            
        #elif empty_tiles >= 0:
         #   max_depth = 6
        else:
            max_depth = 2

    score = calculate_chance(newboard, 0, max_depth)
    return score

# EXPECTIMAX
def calculate_chance(board, curr_depth, max_depth):
    if curr_depth >= max_depth:
       # return n_empty_tiles(board)  #Modify the selected heuristic
       return evaluate(board) #--modified the selected heuristic
  
    possible_boards_2 = []
    possible_boards_4 = []

    for x in range(c.GRID_LEN):
        for y in range(c.GRID_LEN):
            if board[x][y] == 0:
                new_board = copy.deepcopy(board)
                new_board[x][y] = 2
                possible_boards_2.append(new_board)

                new_board = copy.deepcopy(board)
                new_board[x][y] = 4
                possible_boards_4.append(new_board)

    ### Implemented HERE

    if not possible_boards_2 and not possible_boards_4:
        return evaluate(board)
    
    total_score = 0
    count = 0

    # 90% chance for 2
    for b in possible_boards_2:
        total_score += 0.9* calculate_max(b, curr_depth + 1, max_depth)
        count += 1
    
    # 10% chance for 4
    for b in possible_boards_4:
        total_score += 0.1* calculate_max(b, curr_depth + 1, max_depth)
        count += 1
    return total_score / count if count > 0 else evaluate(board)



def calculate_max(board, curr_depth, max_depth):
    if curr_depth >= max_depth:
       # return n_empty_tiles(board)  #Modify the selected heuristic
       return evaluate(board) # modified the selected heuristic

    # best_score = 0
    best_score = - 1000000
        
    for key in commands.keys():
        successor = commands[key](board)[0]
        if board == successor:
            continue
        score = calculate_chance(successor, curr_depth + 1, max_depth)
        if best_score < score:
            best_score = score
    # return best_score
    return best_score if best_score != -1000000 else evaluate(board)


## Heuristics
def n_empty_tiles(matrix):
    return sum(sum(np.array(matrix) == 0))

# Random Choice
def heuristic_random():
    tmp = [c.KEY_UP, c.KEY_DOWN, c.KEY_RIGHT, c.KEY_LEFT]
    key = tmp[random.randint(0, 3)]
    return key


# A Sample Heuristic
def heuristic_empty_tile(matrix):
    best_score = -1
    return_key = None

    for key in commands.keys():
        game, done, points = commands[key](matrix)

        if not done:
            pass

        if done:
            n_empty = n_empty_tiles(game)
            if n_empty > best_score:
                best_score = n_empty
                return_key = key

    return return_key

### Implement HERE
def heuristic_empty_tile(board):
    return n_empty_tiles(board)


def heuristic_max_tile(board):
    return max(max(row) for row in board)


def heuristic_monotonocity(board):
    score = 0
    for row in board:
        for i in range(len(row) - 1):
            if row[i] >= row[i + 1]:
                score += 1
            else:
                score -= 1
    for j in range(len(board[0])):
        for i in range(len(board) - 1):
            if board[i][j] >= board[i + 1][j]:
                score += 1
            else:
                score -= 1
    return score


def heuristic_smoothness(board):
    score = 0
    for i in range(len(board)):
        for j in range(len(board[0]) - 1):
            score -= abs(board[i][j] - board[i][j + 1])
    for j in range(len(board[0])):
        for i in range(len(board) - 1):
            score -= abs(board[i][j] - board[i + 1][j])
    return -score


def heuristic_combined(board):
    return (
        2.5 * heuristic_empty_tile(board) +
        1.5 * heuristic_max_tile(board) +
        1.0 * heuristic_monotonocity(board) +
        0.5 * heuristic_smoothness(board)
    )

def evaluate(board):
    if CURRENT_HEURISTIC == "empty_tile":
        return heuristic_empty_tile(board)
    elif CURRENT_HEURISTIC == "max_tile":
        return heuristic_max_tile(board)
    elif CURRENT_HEURISTIC == "monotonicity":
        return heuristic_monotonocity(board)
    elif CURRENT_HEURISTIC == "smoothness":
        return heuristic_smoothness(board)
    elif CURRENT_HEURISTIC == "combined":
        return heuristic_combined(board)
    else:
        return heuristic_empty_tile(board)
