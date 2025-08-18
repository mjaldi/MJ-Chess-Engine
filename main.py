import pygame
import random
# Screen settings
screen_width = 1000
screen_height = 1000
screen = pygame.display.set_mode((screen_width, screen_height), pygame.DOUBLEBUF)
pygame.display.set_caption("Chess")

# Colors
white = (255, 255, 255)
black = (0, 0, 0)
dark_purple = (77,109,146)
light_purple = (236,236,215)

# Chess Board
chess_board = [
    "bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR",
    "bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP",
    "-", "-", "-", "-", "-", "-", "-", "-",
    "-", "-", "-", "-", "-", "-", "-", "-",
    "-", "-", "-", "-", "-", "-", "-", "-",
    "-", "-", "-", "-", "-", "-", "-", "-",
    "wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP",
    "wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"
]

# Draw chess board
def draw_chess_board():
    for i in range(8):
        for j in range(8):
            if (i+j) % 2 == 0:
                pygame.draw.rect(screen, light_purple, (i*100+100, j*100+100, 100, 100))
            else:
                pygame.draw.rect(screen, dark_purple, (i*100+100, j*100+100, 100, 100))

#Draw piece
def draw_piece(piece, pos):
    data = pygame.image.load("images/" + piece + ".png")
    data = pygame.transform.scale(data, (100, 100))
    screen.blit(data, (pos))

# Loop through the chess board and draw the pieces
def refresh_pieces(exclude=None):
    for index, piece in enumerate(chess_board):
        if piece != "-" and index != exclude:
            row = index // 8
            col = index % 8
            draw_piece(piece, (col * 100 + 100, row * 100 + 100))

last_move = None

# Move piece
def move_piece(pos, move):
    global last_move
    piece = chess_board[pos]
    target = pos + move
    # Castling
    if chess_board[pos] == "wK":
        if pos == 60:
            if move == 2:
                chess_board[63] = "-"
                chess_board[61] = "wR"
            if move == -2:
                chess_board[56] = "-"
                chess_board[59] = "wR"
    if chess_board[pos] == "bK":
        if pos == 4:
            if move == 2:
                chess_board[7] = "-"
                chess_board[5] = "bR"
            if move == -2:
                chess_board[0] = "-"
                chess_board[3] = "bR"
    
    # En passant
    if chess_board[pos][-1] == "P":
        if abs(move) == 16:
            last_move = (pos, target)
        else:
            last_move = None
        if abs(move) in [7, 9] and chess_board[target] == "-":
            if piece[0] == "w":
                chess_board[target - 8] = "-"
            else:
                chess_board[target + 8] = "-"
    chess_board[pos+move] = chess_board[pos]
    chess_board[pos] = "-"
    if piece == "wP" and target < 8:
        chess_board[target] = "wQ"
    if piece == "bP" and target > 55:
        chess_board[target] = "bQ"

def get_board_pos(mouse_pos):
    x, y = mouse_pos
    row = (y - 100) // 100
    col = (x - 100) // 100
    return row * 8 + col

def simulate_move(board, pos, move):
    new_board = board.copy()
    new_board[pos + move] = new_board[pos]
    new_board[pos] = "-"
    return new_board

def get_moves(pos):
    piece = chess_board[pos]
    moves = []
    if piece[-1] == "P":
        moves= get_pawn_moves(pos, chess_board)
    elif piece[-1] == "R":
        moves= get_rook_moves(pos, chess_board)
    elif piece[-1] == "N":
        moves= get_knight_moves(pos, chess_board)
    elif piece[-1] == "B":
        moves= get_bishop_moves(pos, chess_board)
    elif piece[-1] == "Q":
        moves= get_queen_moves(pos, chess_board)
    elif piece[-1] == "K":
        moves= get_king_moves(pos, chess_board)
    print(moves)
    valid_moves = []
    for move in moves:
        new_board = simulate_move(chess_board, pos, move)
        if not check_status(new_board, piece[0]):
            valid_moves.append(move)
    print(valid_moves)
    return valid_moves

def get_pawn_moves(pos, board):
    moves = []
    color = board[pos][0]
    direction = -8 if color == "w" else 8
    start_row = 6 if color == "w" else 1

    # Forward move
    if board[pos + direction] == "-":
        moves.append(direction)
        # Initial 2-tile jump
        if (pos // 8 == start_row) and board[pos + 2 * direction] == "-":
            moves.append(2 * direction)

    # Captures
    for diag in [-9, -7] if color == "w" else [7, 9]:
        target = pos + diag
        if 0 <= target < 64 and abs((pos % 8) - (target % 8)) == 1:
            if board[target] != "-" and board[target][0] != color:
                moves.append(diag)
            # Add en passant logic here if needed

    return moves

def get_rook_moves(pos, board):
    moves = []
    for i in range(1, 8):
        if pos + i * 8 < 64:
            if board[pos + i * 8] == "-":
                moves.append(i * 8)
            elif board[pos + i * 8][0] != board[pos][0]:
                moves.append(i * 8)
                break
            else:
                break
    for i in range(1, 8):
        if pos - i * 8 >= 0:
            if board[pos - i * 8] == "-":
                moves.append(-i * 8)
            elif board[pos - i * 8][0] != board[pos][0]:
                moves.append(-i * 8)
                break
            else:
                break
    for i in range(1, 8):
        if pos + i < (pos // 8 + 1) * 8:
            if board[pos + i] == "-":
                moves.append(i)
            elif board[pos + i][0] != board[pos][0]:
                moves.append(i)
                break
            else:
                break
    for i in range(1, 8):
        if pos - i >= pos // 8 * 8:
            if board[pos - i] == "-":
                moves.append(-i)
            elif board[pos - i][0] != board[pos][0]:
                moves.append(-i)
                break
            else:
                break
    return moves

def get_knight_moves(pos, board):
    moves = []
    knight_offsets = [17, 15, 10, 6, -17, -15, -10, -6]
    team_color = chess_board[pos][0]  # 'w' for white, 'b' for black

    for offset in knight_offsets:
        new_pos = pos + offset
        if 0 <= new_pos < 64 and abs((pos % 8) - (new_pos % 8)) in [1, 2]:  # Ensure L-shape within board
            if board[new_pos] == "-" or board[new_pos][0] != team_color:  # Empty or enemy piece
                moves.append(offset)
    
    return moves

def get_bishop_moves(pos,board):
    moves = []
    # Top-right diagonal
    for i in range(1, 8):
        new_pos = pos - i * 7   
        if new_pos >= 0 and (new_pos % 8 != 0):
            if board[new_pos] == "-":
                moves.append(-i * 7)
            elif board[new_pos][0] != board[pos][0]:
                moves.append(-i * 7)
                break
            else:
                break
        else:
            break
    # Top-left diagonal
    for i in range(1, 8):
        new_pos = pos - i * 9
        if new_pos >= 0 and (new_pos % 8 != 7):
            if board[new_pos] == "-":
                moves.append(-i * 9)
            elif board[new_pos][0] != board[pos][0]:
                moves.append(-i * 9)
                break
            else:
                break
        else:
            break
    # Bottom-right diagonal
    for i in range(1, 8):
        new_pos = pos + i * 9
        if new_pos < 64 and (new_pos % 8 != 0):
            if board[new_pos] == "-":
                moves.append(i * 9)
            elif board[new_pos][0] != board[pos][0]:
                moves.append(i * 9)
                break
            else:
                break
        else:
            break
    # Bottom-left diagonal
    for i in range(1, 8):
        new_pos = pos + i * 7
        if new_pos < 64 and (new_pos % 8 != 7):
            if board[new_pos] == "-":
                moves.append(i * 7)
            elif board[new_pos][0] != board[pos][0]:
                moves.append(i * 7)
                break
            else:
                break
        else:
            break
    return moves

def get_queen_moves(pos, board):
    return get_rook_moves(pos, board) + get_bishop_moves(pos, board)

def get_king_moves(pos, board):
    moves = []
    king_color = board[pos][0]
    if king_color  == "w":
        if pos == 60:
            if board[61] == "-" and board[62] == "-" and board[63] == "wR":
                moves.append(2)
            if board[59] == "-" and board[58] == "-" and board[57] == "-" and board[56] == "wR":
                moves.append(-2)
    elif king_color == "b":
        if pos == 4:
            if board[5] == "-" and board[6] == "-" and board[7] == "bR":
                moves.append(2)
            if board[3] == "-" and board[2] == "-" and board[1] == "-" and board[0] == "bR":
                moves.append(-2)
    if pos % 8 != 0: 
        if board[pos - 1] == "-" or board[pos - 1][0] != board[pos][0]:
            moves.append(-1)
        if pos // 8 != 0:
            if board[pos - 9] == "-" or board[pos - 9][0] != board[pos][0]:
                moves.append(-9)
        if pos // 8 != 7:
            if board[pos + 7] == "-" or board[pos + 7][0] != board[pos][0]:
                moves.append(7)
    if pos % 8 != 7:
        if board[pos + 1] == "-" or board[pos + 1][0] != board[pos][0]:
            moves.append(1)
        if pos // 8 != 0:
            if board[pos - 7] == "-" or board[pos - 7][0] != board[pos][0]:
                moves.append(-7)
        if pos // 8 != 7:
            if board[pos + 9] == "-" or board[pos + 9][0] != board[pos][0]:
                moves.append(9)
    if pos // 8 != 0:
        if board[pos - 8] == "-" or board[pos - 8][0] != board[pos][0]:
            moves.append(-8)
    if pos // 8 != 7:
        if board[pos + 8] == "-" or board[pos + 8][0] != board[pos][0]:
            moves.append(8)
    return moves

def danger_squares(board, color):
    squares = []
    for i, piece in enumerate(board):
        if piece != "-" and piece[0] == color:
            moves = []
            if piece[-1] == "P":
                if color == "w":
                    if i % 8 != 0 and i - 9 >= 0:
                        moves.append(-9)
                    if i % 8 != 7 and i - 7 >= 0:
                        moves.append(-7)
                else:
                    if i % 8 != 0 and i + 7 < 64:
                        moves.append(7)
                    if i % 8 != 7 and i + 9 < 64:
                        moves.append(9)
            elif piece[-1] == "R":
                moves = get_rook_moves(i, board)
            elif piece[-1] == "N":
                moves = get_knight_moves(i, board)
            elif piece[-1] == "B":
                moves = get_bishop_moves(i, board)
            elif piece[-1] == "Q":
                moves = get_queen_moves(i, board)
            elif piece[-1] == "K":
                moves = get_king_moves(i, board)
            for move in moves:
                squares.append(i + move)
    return squares

def check_status(board, color):
    king_pos = board.index(color + "K")
    opponent = "b" if color == "w" else "w"
    return king_pos in danger_squares(board,opponent)

def checkmate(color):
    for i, piece in enumerate(chess_board):
        if piece != "-" and piece[0] == color:
            moves = get_moves(i)
            for move in moves:
                temp_board = simulate_move(chess_board, i, move)
                if not check_status(temp_board, color):
                    return False
    return True

# Evaluate the board
def evaluate_board(board):
    piece_values = {"P": 100, "N": 320, "B": 330, "R": 500, "Q": 900, "K": 0}
    score = 0
    for piece in board:
        if piece != "-":
            value = piece_values[piece[1]]
            if piece[0] == "w":
                score += value
            else:
                score -= value
    return score

def flip_table(table):
    return sum([list(table[i*8:(i+1)*8]) for i in reversed(range(8))], [])
def game_over(board):
    if "wK" not in board or "bK" not in board:
        return True
    return False

def is_capture(pos, move, board):
    target = pos + move
    return board[target] != "-"

def minimax(board, depth, alpha, beta, maximizing_player):
    if depth == 0 or game_over(board):
        return evaluate_board(board)

    moves_exist = False
    best_eval = float('-inf') if maximizing_player else float('inf')

    for i, piece in enumerate(board):
        if piece != "-" and ((maximizing_player and piece[0] == "b") or (not maximizing_player and piece[0] == "w")):
            for move in get_moves(i):
                moves_exist = True
                new_board = simulate_move(board, i, move)
                # If this move is a capture, search deeper (quiescence)
                if is_capture(i, move, board):
                    eval = minimax(new_board, depth, alpha, beta, not maximizing_player)
                else:
                    eval = minimax(new_board, depth-1, alpha, beta, not maximizing_player)
                if maximizing_player:
                    best_eval = max(best_eval, eval)
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break
                else:
                    best_eval = min(best_eval, eval)
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break
    if not moves_exist:
        return evaluate_board(board)
    return best_eval

def get_comp_move(depth):
    best_score = float('-inf')
    best_moves = []
    for i, piece in enumerate(chess_board):
        if piece != "-" and piece[0] == "b":
            for move in get_moves(i):
                new_board = simulate_move(chess_board, i, move)
                score = minimax(new_board, depth-1, float('-inf'), float('inf'), False)
                if score > best_score:
                    best_score = score
                    best_moves = [(i, move)]
                elif score == best_score:
                    best_moves.append((i, move))
    if best_moves:
        return random.choice(best_moves)
    return None

# Game loop
running = True
selected_piece = None
dragging = False
turn = "w"
while running:
    screen.fill(black)

    draw_chess_board()
    refresh_pieces(selected_piece if dragging else None)
    if turn == "b":
        # make random move
        move = get_comp_move(2)
        move_piece(move[0], move[1])
        turn = "w"
        
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            pos = get_board_pos(mouse_pos)
            if chess_board[pos] != "-":
                selected_piece = pos
                dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if dragging:
                mouse_pos = pygame.mouse.get_pos()
                new_pos = get_board_pos(mouse_pos)
                move = new_pos - selected_piece
                if move in get_moves(selected_piece) and chess_board[selected_piece][0] == turn:
                    move_piece(selected_piece, move)
                    turn = "b" if turn == "w" else "w"
                dragging = False
                if checkmate("w"):
                    print("Black wins")
                    running = False
                elif checkmate("b"):
                    print("White wins")
                    running = False
                selected_piece = None
        elif event.type == pygame.MOUSEMOTION:
            if dragging:
                mouse_pos = pygame.mouse.get_pos()
                screen.fill(black)
                draw_chess_board()
                refresh_pieces(selected_piece)
                draw_piece(chess_board[selected_piece], (mouse_pos[0] - 50, mouse_pos[1] - 50))
    
    pygame.display.update()

pygame.quit()