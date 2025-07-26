# rollerball_chess.py (Fixing the IndexError in get_piece)
import math

class RollerballBoard:
    def __init__(self):
        self.board = [
            ['r', 'n', 'b', 'q', 'k', 'b', 'n'],
            ['p', 'p', 'p', 'p', 'p', 'p', 'p'],
            ['.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.'],
            ['P', 'P', 'P', 'P', 'P', 'P', 'P'],
            ['R', 'N', 'B', 'Q', 'K', 'B', 'N']
        ]
        self.current_player = 'white'
        self.game_over = False
        self.winner = None

    def print_board(self):
        # This function is not used by gui_game.py, so no change needed here.
        pass

    def is_valid_pos(self, r, c):
        # A simple bounds check for the actual board array
        return 0 <= r < 7 and 0 <= c < 7

    def wrap_coords(self, r, c):
        # Rows do not wrap in standard Rollerball, they are bounded.
        # We need to ensure 'r' always stays within 0-6.
        # Using max(0, min(6, r)) will clamp the row effectively.
        wrapped_r = max(0, min(6, r))
        # Columns wrap from 0 to 6.
        wrapped_c = c % 7
        return wrapped_r, wrapped_c

    def get_piece(self, r, c):
        # Call wrap_coords to get the board-safe indices
        wrapped_r, wrapped_c = self.wrap_coords(r, c)
        # We should NOT need to re-validate here if wrap_coords is perfect,
        # but the error shows that it's still possible for out-of-bounds access
        # This print will tell us the exact values causing the crash
        # print(f"DEBUG_GET_PIECE: Attempting to access board[{wrapped_r}][{wrapped_c}]") # You can uncomment this to debug further if needed
        
        # Adding a final defensive check here just in case, though it implies
        # an issue in wrap_coords or move generation.
        if not self.is_valid_pos(wrapped_r, wrapped_c):
             # This should ideally never be reached if wrap_coords is correct, but for safety:
             raise IndexError(f"Internal error: Wrapped coordinates ({wrapped_r},{wrapped_c}) are out of board bounds.")
             
        return self.board[wrapped_r][wrapped_c]

    def set_piece(self, r, c, piece):
        wrapped_r, wrapped_c = self.wrap_coords(r, c)
        self.board[wrapped_r][wrapped_c] = piece

    def clone(self):
        new_board = RollerballBoard()
        new_board.board = [row[:] for row in self.board]
        new_board.current_player = self.current_player
        new_board.game_over = self.game_over
        new_board.winner = self.winner
        return new_board

    def get_piece_color(self, piece):
        if 'A' <= piece <= 'Z':
            return 'white'
        elif 'a' <= piece <= 'z':
            return 'black'
        return None

    def is_opponent(self, r, c, current_player):
        piece = self.get_piece(r, c) # get_piece will use wrap_coords
        if piece == '.':
            return False
        return self.get_piece_color(piece) != current_player

    def is_friendly(self, r, c, current_player):
        piece = self.get_piece(r, c) # get_piece will use wrap_coords
        if piece == '.':
            return False
        return self.get_piece_color(piece) == current_player

    def find_king(self, player_color):
        king_piece = 'K' if player_color == 'white' else 'k'
        for r in range(7):
            for c in range(7):
                if self.board[r][c] == king_piece:
                    return (r, c)
        return None

    def is_attacked(self, r, c, by_player_color):
        original_current_player = self.current_player
        self.current_player = by_player_color

        attacked = False
        for pr in range(7):
            for pc in range(7):
                piece = self.get_piece(pr, pc) # This call to get_piece can cause the IndexError
                if piece != '.' and self.get_piece_color(piece) == by_player_color:
                    
                    if piece.upper() == 'P':
                        direction = 1 if by_player_color == 'white' else -1 # Pawns attack "backwards" from attacker's perspective
                        for dc in [-1, 1]:
                            target_r, target_c = self.wrap_coords(pr + direction, pc + dc)
                            # IMPORTANT: Check validity AFTER wrap_coords, BEFORE using the coordinates.
                            if self.is_valid_pos(target_r, target_c) and (target_r, target_c) == (r, c):
                                attacked = True
                                break
                    elif piece.upper() == 'R':
                        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                            for i in range(1, 7):
                                target_r, target_c = self.wrap_coords(pr + dr * i, pc + dc * i)
                                if not self.is_valid_pos(target_r, target_c): # Break if outside valid board range
                                    break
                                if (target_r, target_c) == (r, c):
                                    attacked = True
                                    break
                                # get_piece here will use the validated target_r, target_c
                                if self.get_piece(target_r, target_c) != '.':
                                    break
                            if attacked: break
                    elif piece.upper() == 'N':
                        knight_moves = [
                            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
                            (1, -2), (1, 2), (2, -1), (2, 1)
                        ]
                        for dr, dc in knight_moves:
                            target_r, target_c = self.wrap_coords(pr + dr, pc + dc)
                            if not self.is_valid_pos(target_r, target_c): # Continue if outside valid board range
                                continue
                            if (target_r, target_c) == (r, c):
                                attacked = True
                                break
                        if attacked: break
                    elif piece.upper() == 'B':
                        for dr, dc in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
                            for i in range(1, 7):
                                target_r, target_c = self.wrap_coords(pr + dr * i, pc + dc * i)
                                if not self.is_valid_pos(target_r, target_c): # Break if outside valid board range
                                    break
                                if (target_r, target_c) == (r, c):
                                    attacked = True
                                    break
                                if self.get_piece(target_r, target_c) != '.':
                                    break
                            if attacked: break
                    elif piece.upper() == 'Q':
                        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
                            for i in range(1, 7):
                                target_r, target_c = self.wrap_coords(pr + dr * i, pc + dc * i)
                                if not self.is_valid_pos(target_r, target_c): # Break if outside valid board range
                                    break
                                if (target_r, target_c) == (r, c):
                                    attacked = True
                                    break
                                if self.get_piece(target_r, target_c) != '.':
                                    break
                            if attacked: break
                    elif piece.upper() == 'K':
                        for dr in [-1, 0, 1]:
                            for dc in [-1, 0, 1]:
                                if dr == 0 and dc == 0: continue
                                target_r, target_c = self.wrap_coords(pr + dr, pc + dc)
                                if not self.is_valid_pos(target_r, target_c): # Continue if outside valid board range
                                    continue
                                if (target_r, target_c) == (r, c):
                                    attacked = True
                                    break
                            if attacked: break
                if attacked: break
            if attacked: break

        self.current_player = original_current_player
        return attacked

    def is_in_check(self, player_color):
        king_pos = self.find_king(player_color)
        if king_pos:
            opponent_color = 'white' if player_color == 'black' else 'black'
            # This call to is_attacked will now use more robust checks
            return self.is_attacked(king_pos[0], king_pos[1], opponent_color)
        return True # King not found, implies captured or invalid state

    def get_legal_moves(self, r, c):
        piece = self.get_piece(r, c)
        if piece == '.':
            return []

        player_color = self.get_piece_color(piece)
        if player_color != self.current_player:
            return []

        moves = []

        def add_pseudo_move(target_r, target_c):
            # Pass already wrapped and valid coordinates to this helper
            if self.is_valid_pos(target_r, target_c): # Final check
                if self.get_piece(target_r, target_c) == '.' or \
                   self.is_opponent(target_r, target_c, player_color):
                    moves.append(((r, c), (target_r, target_c)))

        if piece.upper() == 'P':
            direction = -1 if player_color == 'white' else 1
            
            # Forward move
            target_r, target_c = self.wrap_coords(r + direction, c)
            if self.is_valid_pos(target_r, target_c) and self.get_piece(target_r, target_c) == '.':
                add_pseudo_move(target_r, target_c)
            
            # Captures
            for dc in [-1, 1]:
                target_r, target_c = self.wrap_coords(r + direction, c + dc)
                if self.is_valid_pos(target_r, target_c) and self.is_opponent(target_r, target_c, player_color):
                    add_pseudo_move(target_r, target_c)

        elif piece.upper() == 'R':
            for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                for i in range(1, 7):
                    target_r, target_c = self.wrap_coords(r + dr * i, c + dc * i)
                    if not self.is_valid_pos(target_r, target_c): break
                    if self.get_piece(target_r, target_c) == '.':
                        add_pseudo_move(target_r, target_c)
                    elif self.is_opponent(target_r, target_c, player_color):
                        add_pseudo_move(target_r, target_c)
                        break
                    else:
                        break

        elif piece.upper() == 'N':
            knight_moves = [
                (-2, -1), (-2, 1), (-1, -2), (-1, 2),
                (1, -2), (1, 2), (2, -1), (2, 1)
            ]
            for dr, dc in knight_moves:
                target_r, target_c = self.wrap_coords(r + dr, c + dc)
                if not self.is_valid_pos(target_r, target_c): continue
                if not self.is_friendly(target_r, target_c, player_color):
                    add_pseudo_move(target_r, target_c)

        elif piece.upper() == 'B':
            for dr, dc in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
                for i in range(1, 7):
                    target_r, target_c = self.wrap_coords(r + dr * i, c + dc * i)
                    if not self.is_valid_pos(target_r, target_c): break
                    if self.get_piece(target_r, target_c) == '.':
                        add_pseudo_move(target_r, target_c)
                    elif self.is_opponent(target_r, target_c, player_color):
                        add_pseudo_move(target_r, target_c)
                        break
                    else:
                        break

        elif piece.upper() == 'Q':
            for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
                for i in range(1, 7):
                    target_r, target_c = self.wrap_coords(r + dr * i, c + dc * i)
                    if not self.is_valid_pos(target_r, target_c): break
                    if self.get_piece(target_r, target_c) == '.':
                        add_pseudo_move(target_r, target_c)
                    elif self.is_opponent(target_r, target_c, player_color):
                        add_pseudo_move(target_r, target_c)
                        break
                    else:
                        break

        elif piece.upper() == 'K':
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    target_r, target_c = self.wrap_coords(r + dr, c + dc)
                    if not self.is_valid_pos(target_r, target_c): continue
                    if not self.is_friendly(target_r, target_c, player_color):
                        add_pseudo_move(target_r, target_c)

        return moves

    def get_all_legal_moves(self):
        all_pseudo_moves = []
        for r in range(7):
            for c in range(7):
                piece = self.get_piece(r, c)
                if piece != '.' and self.get_piece_color(piece) == self.current_player:
                    moves_for_piece = self.get_legal_moves(r, c)
                    all_pseudo_moves.extend(moves_for_piece)
        
        valid_moves = []
        for start, end in all_pseudo_moves:
            temp_board = self.clone()
            original_piece = temp_board.get_piece(start[0], start[1])
            
            temp_board.set_piece(end[0], end[1], original_piece)
            temp_board.set_piece(start[0], start[1], '.')

            if not temp_board.is_in_check(self.current_player):
                valid_moves.append((start, end))
        return valid_moves

    def make_move(self, start_pos, end_pos):
        r1, c1 = start_pos
        r2, c2 = end_pos

        piece = self.get_piece(r1, c1)
        if piece == '.':
            return False

        if self.get_piece_color(piece) != self.current_player:
            return False

        all_legal_moves_for_current_player = self.get_all_legal_moves()
        
        if (start_pos, end_pos) not in all_legal_moves_for_current_player:
            return False

        self.set_piece(r2, c2, piece)
        self.set_piece(r1, c1, '.')

        if piece.upper() == 'P':
            if (self.current_player == 'white' and r2 == 0) or \
               (self.current_player == 'black' and r2 == 6):
                self.set_piece(r2, c2, 'Q' if self.current_player == 'white' else 'q')

        self.current_player = 'black' if self.current_player == 'white' else 'white'

        self.check_game_over()

        return True

    def check_game_over(self):
        legal_moves_for_next_player = self.get_all_legal_moves()

        if not legal_moves_for_next_player:
            if self.is_in_check(self.current_player):
                self.game_over = True
                self.winner = 'white' if self.current_player == 'black' else 'black'
            else:
                self.game_over = True
                self.winner = 'draw'
        
        if not self.find_king('white'):
            self.game_over = True
            self.winner = 'black'
        if not self.find_king('black'):
            self.game_over = True
            self.winner = 'white'

    def evaluate_board(self, player_color_for_eval):
        score = 0
        piece_values = {
            'P': 10, 'N': 30, 'B': 30, 'R': 50, 'Q': 90, 'K': 900,
            'p': -10, 'n': -30, 'b': -30, 'r': -50, 'q': -90, 'k': -900
        }

        pawn_pst = [
            [0,  0,  0,  0,  0,  0,  0],
            [50, 50, 50, 50, 50, 50, 50],
            [10, 10, 20, 30, 20, 10, 10],
            [ 5,  5, 10, 25, 10,  5,  5],
            [ 0,  0,  0, 20,  0,  0,  0],
            [ 5, -5,-10,  0, -10, -5,  5],
            [ 0,  0,  0,  0,  0,  0,  0]
        ]

        knight_pst = [
            [-50,-40,-30,-30,-30,-40,-50],
            [-40,-20,  0,  0,  0,-20,-40],
            [-30,  0, 10, 15, 10,  0,-30],
            [-30,  5, 15, 20, 15,  5,-30],
            [-30,  0, 15, 20, 15,  0,-30],
            [-40,-20,  0,  5,  0,-20,-40],
            [-50,-40,-30,-30,-30,-40,-50]
        ]

        bishop_pst = [
            [-20,-10,-10,-10,-10,-10,-20],
            [-10,  0,  0,  0,  0,  0,-10],
            [-10,  0,  5, 10,  5,  0,-10],
            [-10,  5,  5, 10,  5,  5,-10],
            [-10,  0, 10, 10, 10,  0,-10],
            [-10, 10,  0,  0,  0, 10,-10],
            [-20,-10,-10,-10,-10,-10,-20]
        ]

        rook_pst = [
            [ 0,  0,  0,  5,  0,  0,  0],
            [-5,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0, -5],
            [ 0,  0,  0,  5,  0,  0,  0]
        ]

        queen_pst = [
            [-20,-10,-10, -5, -10,-10,-20],
            [-10,  0,  0,  0,  0,  0,-10],
            [-10,  0,  5,  5,  5,  0,-10],
            [ -5,  0,  5,  5,  5,  0, -5],
            [  0,  0,  5,  5,  5,  0, -5],
            [-10,  5,  0,  0,  0,  5,-10],
            [-20,-10,-10, -5,-10,-10,-20]
        ]

        king_pst_middle_game = [
            [-30,-40,-40,-50,-40,-40,-30],
            [-30,-40,-40,-50,-40,-40,-30],
            [-30,-40,-40,-50,-40,-40,-30],
            [-30,-40,-40,-50,-40,-40,-30],
            [-20,-30,-30,-40,-30,-30,-20],
            [-10,-20,-20,-20,-20,-20,-10],
            [ 20, 30, 10,  0, 10, 30, 20]
        ]

        king_pst_end_game = [
            [-50,-40,-30,-20,-30,-40,-50],
            [-30,-20,-10,  0,-10,-20,-30],
            [-30,-10, 20, 30, 20,-10,-30],
            [-30,-10, 30, 40, 30,-10,-30],
            [-30,-10, 30, 40, 30,-10,-30],
            [-30,-20,-10,  0,-10,-20,-30],
            [-50,-40,-30,-20,-30,-40,-50]
        ]

        num_queens = 0
        for r_idx in range(7):
            for c_idx in range(7):
                piece = self.board[r_idx][c_idx]
                if piece.upper() == 'Q':
                    num_queens += 1
        
        is_endgame = num_queens <= 1

        # --- Evaluation Logic ---

        # 1. Material Advantage & PST
        for r_idx in range(7):
            for c_idx in range(7):
                piece = self.board[r_idx][c_idx]
                if piece == '.':
                    continue

                piece_color = self.get_piece_color(piece)
                is_white = (piece_color == 'white')
                
                score += piece_values.get(piece, 0)

                pst_value = 0
                r_effective = r_idx if is_white else 6 - r_idx
                
                if piece.upper() == 'P':
                    pst_value = pawn_pst[r_effective][c_idx]
                elif piece.upper() == 'N':
                    pst_value = knight_pst[r_effective][c_idx]
                elif piece.upper() == 'B':
                    pst_value = bishop_pst[r_effective][c_idx]
                elif piece.upper() == 'R':
                    pst_value = rook_pst[r_effective][c_idx]
                elif piece.upper() == 'Q':
                    pst_value = queen_pst[r_effective][c_idx]
                elif piece.upper() == 'K':
                    if is_endgame:
                        pst_value = king_pst_end_game[r_effective][c_idx]
                    else:
                        pst_value = king_pst_middle_game[r_effective][c_idx]
                
                score += pst_value if is_white else -pst_value

        # 2. Pawn Structure
        for c_idx in range(7):
            white_pawns_on_file = sum(1 for r_idx in range(7) if self.board[r_idx][c_idx] == 'P')
            black_pawns_on_file = sum(1 for r_idx in range(7) if self.board[r_idx][c_idx] == 'p')
            
            if white_pawns_on_file > 1:
                score -= (white_pawns_on_file - 1) * 10
            if black_pawns_on_file > 1:
                score += (black_pawns_on_file - 1) * 10

        for c_idx in range(7):
            has_white_pawn = any(self.board[r_idx][c_idx] == 'P' for r_idx in range(7))
            if has_white_pawn:
                left_file_has_white_pawn = any(self.board[r_idx][self.wrap_coords(0, c_idx - 1)[1]] == 'P' for r_idx in range(7))
                right_file_has_white_pawn = any(self.board[r_idx][self.wrap_coords(0, c_idx + 1)[1]] == 'P' for r_idx in range(7))
                if not left_file_has_white_pawn and not right_file_has_white_pawn:
                    score -= 5

            has_black_pawn = any(self.board[r_idx][c_idx] == 'p' for r_idx in range(7))
            if has_black_pawn:
                left_file_has_black_pawn = any(self.board[r_idx][self.wrap_coords(0, c_idx - 1)[1]] == 'p' for r_idx in range(7))
                right_file_has_black_pawn = any(self.board[r_idx][self.wrap_coords(0, c_idx + 1)[1]] == 'p' for r_idx in range(7))
                if not left_file_has_black_pawn and not right_file_has_black_pawn:
                    score += 5

        for r_idx in range(7):
            for c_idx in range(7):
                piece = self.board[r_idx][c_idx]
                if piece == 'P':
                    is_passed = True
                    for check_r in range(r_idx):
                        for check_c_offset in [-1, 0, 1]:
                            check_c = self.wrap_coords(0, c_idx + check_c_offset)[1]
                            if self.board[check_r][check_c] == 'p':
                                is_passed = False
                                break
                        if not is_passed: break
                    if is_passed:
                        score += 20 + (6 - r_idx) * 5
                elif piece == 'p':
                    is_passed = True
                    for check_r in range(r_idx + 1, 7):
                        for check_c_offset in [-1, 0, 1]:
                            check_c = self.wrap_coords(0, c_idx + check_c_offset)[1]
                            if self.board[check_r][check_c] == 'P':
                                is_passed = False
                                break
                        if not is_passed: break
                    if is_passed:
                        score -= (20 + r_idx * 5)

        # 3. Mobility (Number of legal moves available to a player)
        original_current_player = self.current_player
        
        self.current_player = 'white'
        white_mobility_count = len(self.get_all_legal_moves())
        score += white_mobility_count * 0.1

        self.current_player = 'black'
        black_mobility_count = len(self.get_all_legal_moves())
        score -= black_mobility_count * 0.1

        self.current_player = original_current_player

        # 4. King Safety (more comprehensive)
        white_king_pos = self.find_king('white')
        if white_king_pos:
            r, c = white_king_pos
            white_pawns_on_file_left = any(self.board[pr][self.wrap_coords(0, c - 1)[1]] == 'P' for pr in range(r, 7))
            white_pawns_on_file_right = any(self.board[pr][self.wrap_coords(0, c + 1)[1]] == 'P' for pr in range(r, 7))
            white_pawns_on_current_file = any(self.board[pr][c] == 'P' for pr in range(r, 7))
            
            if not white_pawns_on_current_file:
                score -= 10
            if not white_pawns_on_file_left and not white_pawns_on_file_right:
                 score -= 15

            pawn_shield_score = 0
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0: continue
                    adj_r, adj_c = self.wrap_coords(r + dr, c + dc)
                    if self.is_valid_pos(adj_r, adj_c) and self.get_piece(adj_r, adj_c) == 'P':
                        pawn_shield_score += 1
            score += pawn_shield_score * 5

        black_king_pos = self.find_king('black')
        if black_king_pos:
            r, c = black_king_pos
            black_pawns_on_file_left = any(self.board[pr][self.wrap_coords(0, c - 1)[1]] == 'p' for pr in range(r + 1))
            black_pawns_on_file_right = any(self.board[pr][self.wrap_coords(0, c + 1)[1]] == 'p' for pr in range(r + 1))
            black_pawns_on_current_file = any(self.board[pr][c] == 'p' for pr in range(r + 1))

            if not black_pawns_on_current_file:
                score += 10
            if not black_pawns_on_file_left and not black_pawns_on_file_right:
                 score += 15

            pawn_shield_score = 0
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0: continue
                    adj_r, adj_c = self.wrap_coords(r + dr, c + dc)
                    if self.is_valid_pos(adj_r, adj_c) and self.get_piece(adj_r, adj_c) == 'p':
                        pawn_shield_score += 1
            score -= pawn_shield_score * 5

        if player_color_for_eval == 'black':
            score = -score

        return score