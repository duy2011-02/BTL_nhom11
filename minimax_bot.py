import copy
import math

class MinimaxBot:
    def __init__(self, depth=2):
        self.depth = depth

    def get_move(self, board, player):
        best_score = -math.inf
        best_move = None
        for move in self.get_possible_moves(board):
            new_board = copy.deepcopy(board)
            new_board[move[0]][move[1]] = player
            score = self.minimax(new_board, self.depth - 1, False, player)
            if score > best_score:
                best_score = score
                best_move = move
        return best_move

    def minimax(self, board, depth, is_maximizing, player):
        opponent = 'O' if player == 'X' else 'X'
        if self.check_winner(board, player):
            return 1000
        if self.check_winner(board, opponent):
            return -1000
        if self.check_draw(board) or depth == 0:
            return 0

        if is_maximizing:
            max_eval = -math.inf
            for move in self.get_possible_moves(board):
                new_board = copy.deepcopy(board)
                new_board[move[0]][move[1]] = player
                eval = self.minimax(new_board, depth - 1, False, player)
                max_eval = max(max_eval, eval)
            return max_eval
        else:
            min_eval = math.inf
            for move in self.get_possible_moves(board):
                new_board = copy.deepcopy(board)
                new_board[move[0]][move[1]] = opponent
                eval = self.minimax(new_board, depth - 1, True, player)
                min_eval = min(min_eval, eval)
            return min_eval

    def get_possible_moves(self, board):
        moves = []
        for i in range(len(board)):
            for j in range(len(board[0])):
                if board[i][j] == ' ':
                    moves.append((i, j))
        return moves

    def check_winner(self, board, player):
        for i in range(len(board)):
            for j in range(len(board[0])):
                if self.check_direction(board, i, j, 0, 1, player) \
                   or self.check_direction(board, i, j, 1, 0, player) \
                   or self.check_direction(board, i, j, 1, 1, player) \
                   or self.check_direction(board, i, j, 1, -1, player):
                    return True
        return False

    def check_direction(self, board, row, col, delta_row, delta_col, player):
        count = 0
        for _ in range(5):
            if 0 <= row < len(board) and 0 <= col < len(board[0]) and board[row][col] == player:
                count += 1
                row += delta_row
                col += delta_col
            else:
                break
        return count == 5

    def check_draw(self, board):
        for row in board:
            if ' ' in row:
                return False
        return True
