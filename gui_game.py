# gui_game.py (DO NOT RUN DIRECTLY IN COLAB - RUN LOCALLY)

import pygame
import sys
import os

# Assuming rollerball_chess.py and ai_player.py are in the same directory
from rollerball_chess import RollerballBoard
from ai_player import AIPlayer

# --- Pygame Setup ---
pygame.init()

# Screen dimensions
BOARD_SIZE = 7 # 7x7 board
SQUARE_SIZE = 80 # Size of each square in pixels
BOARD_WIDTH = BOARD_SIZE * SQUARE_SIZE
BOARD_HEIGHT = BOARD_SIZE * SQUARE_SIZE
SCREEN_DIMENSIONS = (BOARD_WIDTH, BOARD_HEIGHT)

# Colors
LIGHT_SQUARE = (238, 238, 210) # Off-white
DARK_SQUARE = (118, 150, 86) # Green-brown
HIGHLIGHT_COLOR = (255, 255, 0, 100) # Yellow with transparency for highlights

# Set up the display
screen = pygame.display.set_mode(SCREEN_DIMENSIONS)
pygame.display.set_caption("Rollerball Chess AI")

# --- Load Piece Images ---
# You'll need to create a 'pieces' directory and put chess piece images in it.
# Example: wP.png (white pawn), bR.png (black rook), etc.
# Download free chess piece images (e.g., from Wikimedia Commons or Lichess asset packs)
# and resize them to SQUARE_SIZE.
PIECE_IMAGES = {}
piece_filenames = {
    'r': 'bR.jpg', 'n': 'bN.jpg', 'b': 'bB.jpg', 'q': 'bQ.jpg', 'k': 'bK.jpg', 'p': 'bP.jpg',
    'R': 'wR.jpg', 'N': 'wN.jpg', 'B': 'wB.jpg', 'Q': 'wQ.jpg', 'K': 'wK.jpg', 'P': 'wP.jpg'
}

for piece_char, filename in piece_filenames.items():
    try:
        path = os.path.join('pieces', filename)
        image = pygame.image.load(path).convert_alpha()
        PIECE_IMAGES[piece_char] = pygame.transform.scale(image, (SQUARE_SIZE, SQUARE_SIZE))
    except pygame.error as e:
        print(f"Error loading image {filename}: {e}")
        print("Make sure you have a 'pieces' folder in the same directory as gui_game.py")
        print("And that it contains images named like bR.png, wK.png, etc.")
        sys.exit()

# --- Game State Variables ---
game_board = RollerballBoard()
ai_player = AIPlayer(depth=3) # AI depth

selected_square = None # (row, col) of the currently selected piece
valid_moves_for_selected = [] # List of (from_sq, to_sq) tuples for the selected piece

# --- Drawing Functions ---
def draw_board():
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            color = LIGHT_SQUARE if (r + c) % 2 == 0 else DARK_SQUARE
            pygame.draw.rect(screen, color, (c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def draw_pieces():
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            piece_char = game_board.get_piece(r, c)
            if piece_char != '.':
                screen.blit(PIECE_IMAGES[piece_char], (c * SQUARE_SIZE, r * SQUARE_SIZE))

def highlight_squares():
    if selected_square:
        r, c = selected_square
        # Highlight selected square
        s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA) # Create a transparent surface
        s.fill(HIGHLIGHT_COLOR)
        screen.blit(s, (c * SQUARE_SIZE, r * SQUARE_SIZE))
        
        # Highlight valid target squares
        for _, target_sq in valid_moves_for_selected:
            tr, tc = target_sq
            s_target = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            s_target.fill((0, 255, 0, 100)) # Green highlight for legal moves
            screen.blit(s_target, (tc * SQUARE_SIZE, tr * SQUARE_SIZE))


# --- Main Game Loop ---
running = True
ai_thinking = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if not ai_thinking and game_board.current_player == 'white': # Human's turn
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                clicked_row, clicked_col = my // SQUARE_SIZE, mx // SQUARE_SIZE
                
                if selected_square: # A piece is already selected
                    # Try to move the selected piece to the clicked square
                    move = (selected_square, (clicked_row, clicked_col))
                    if game_board.make_move(selected_square, (clicked_row, clicked_col)):
                        print(f"Human moved from {selected_square} to {(clicked_row, clicked_col)}")
                        # Move made, clear selection and prepare for AI turn
                        selected_square = None
                        valid_moves_for_selected = []
                        ai_thinking = True # Signal AI to make its move
                    else:
                        # Illegal move attempt
                        print("Illegal move. Please try again.")
                        selected_square = None # Clear selection for new attempt
                        valid_moves_for_selected = []
                else: # No piece selected, try to select one
                    piece = game_board.get_piece(clicked_row, clicked_col)
                    if piece != '.' and game_board.get_piece_color(piece) == 'white':
                        selected_square = (clicked_row, clicked_col)
                        # Generate and store valid moves for the selected piece to highlight
                        # NOTE: game_board.get_all_legal_moves() gets ALL moves for the current player
                        # We need to filter this for the selected piece.
                        all_legal_moves = game_board.get_all_legal_moves()
                        valid_moves_for_selected = [m for m in all_legal_moves if m[0] == selected_square]
                    else:
                        selected_square = None # Clicked empty square or opponent's piece
                        valid_moves_for_selected = []

    # AI's Turn (Outside event loop to allow AI to think)
    if ai_thinking and game_board.current_player == 'black':
        print("AI is thinking...")
        pygame.time.wait(500) # Small visual pause
        best_move = ai_player.find_best_move(game_board)
        if best_move:
            print(f"AI chose move: {best_move[0]} to {best_move[1]}")
            game_board.make_move(best_move[0], best_move[1])
        else:
            print("AI has no legal moves. Game might be over.")
            game_board.check_game_over() # Ensure game_over state is updated

        ai_thinking = False # AI finished its turn

    # Drawing
    draw_board()
    highlight_squares() # Draw highlights after board, before pieces
    draw_pieces()
    
    # Check for game over (and display message)
    if game_board.game_over:
        font = pygame.font.Font(None, 74)
        message = ""
        if game_board.winner == 'draw':
            message = "Draw!"
        elif game_board.winner:
            message = f"{game_board.winner.upper()} Wins!"
        
        text_surface = font.render(message, True, (255, 0, 0)) # Red text
        text_rect = text_surface.get_rect(center=(BOARD_WIDTH // 2, BOARD_HEIGHT // 2))
        screen.blit(text_surface, text_rect)

    pygame.display.flip() # Update the full display

    # Optionally, allow restarting the game
    if game_board.game_over and not ai_thinking:
        # After game over, wait for a short period and then offer to restart
        # For simplicity in this template, we'll just exit.
        # In a real game, you'd add buttons or a prompt.
        pass # Keep game over message on screen until quit

# Quit Pygame
pygame.quit()
sys.exit()