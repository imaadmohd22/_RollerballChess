import math

class AIPlayer:
    def __init__(self, depth):
        self.depth = depth

    def minimax(self, board, depth, alpha, beta, maximizing_player):
        board.check_game_over()

        if board.game_over:
            if board.winner == 'white':
                return 1000000
            elif board.winner == 'black':
                return -1000000
            else:
                return 0
        
        if depth == 0:
            return board.evaluate_board('white' if maximizing_player else 'black')


        if maximizing_player:
            max_eval = -math.inf
            for move in board.get_all_legal_moves():
                temp_board = board.clone()
                temp_board.make_move(move[0], move[1])
                
                eval = self.minimax(temp_board, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = math.inf
            for move in board.get_all_legal_moves():
                temp_board = board.clone()
                temp_board.make_move(move[0], move[1])
                
                eval = self.minimax(temp_board, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def find_best_move(self, board):
        best_move = None
        max_eval = -math.inf
        alpha = -math.inf
        beta = math.inf

        legal_moves = board.get_all_legal_moves()
        if not legal_moves:
            return None

        for move in legal_moves:
            temp_board = board.clone()
            temp_board.make_move(move[0], move[1]) 
            
            eval = self.minimax(temp_board, self.depth - 1, alpha, beta, False) 
            
            if eval > max_eval:
                max_eval = eval
                best_move = move
            alpha = max(alpha, eval) 

        return best_move