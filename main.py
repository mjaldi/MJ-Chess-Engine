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
    # En passant
    if last_move:
        if board[pos][-1] == "P":
            if pos % 8 != 0 and pos - 1 == last_move[1]:
                if pos // 8 == 3 and board[pos][0] == "w":
                    moves.append(-9)
                    board[pos-1] = "-"
                if pos // 8 == 4 and board[pos][0] == "b":
                    moves.append(7)
                    board[pos-1] = "-"
            if pos % 8 != 7 and pos + 1 == last_move[1]:
                if pos // 8 == 3 and board[pos][0] == "w":
                    moves.append(-7)
                    board[pos+1] = "-"
                if pos // 8 == 4 and board[pos][0] == "b":
                    moves.append(9)
                    board[pos+1] = "-"
            
                moves.append(9)
    if board[pos][0] == "w":
        if board[pos-8] == "-":
            moves.append(-8)
        if pos // 8 == 6 and board[pos-16] == "-":
            moves.append(-16)
        if pos % 8 != 0 and board[pos-9][0] == "b":
            moves.append(-9)
        if pos % 8 != 7 and board[pos-7][0] == "b":
            moves.append(-7)
    else:
        if board[pos+8] == "-":
            moves.append(8)
        if pos // 8 == 1:
            moves.append(16)
        if pos % 8 != 0 and board[pos-9][0] == "w":
            moves.append(9)
        if pos % 8 != 7 and board[pos-7][0] == "w":
            moves.append(7)
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
    piece_values = {"P": 100, "N": 280, "B": 320, "R": 479, "Q": 929, "K": 60000}
    white_piece_tables = {
    'P': (   0,   0,   0,   0,   0,   0,   0,   0,
            78,  83,  86,  73, 102,  82,  85,  90,
             7,  29,  21,  44,  40,  31,  44,   7,
           -17,  16,  -2,  15,  14,   0,  15, -13,
           -26,   3,  10,   9,   6,   1,   0, -23,
           -22,   9,   5, -11, -10,  -2,   3, -19,
           -31,   8,  -7, -37, -36, -14,   3, -31,
             0,   0,   0,   0,   0,   0,   0,   0),
    'N': ( -66, -53, -75, -75, -10, -55, -58, -70,
            -3,  -6, 100, -36,   4,  62,  -4, -14,
            10,  67,   1,  74,  73,  27,  62,  -2,
            24,  24,  45,  37,  33,  41,  25,  17,
            -1,   5,  31,  21,  22,  35,   2,   0,
           -18,  10,  13,  22,  18,  15,  11, -14,
           -23, -15,   2,   0,   2,   0, -23, -20,
           -74, -23, -26, -24, -19, -35, -22, -69),
    'B': ( -59, -78, -82, -76, -23,-107, -37, -50,
           -11,  20,  35, -42, -39,  31,   2, -22,
            -9,  39, -32,  41,  52, -10,  28, -14,
            25,  17,  20,  34,  26,  25,  15,  10,
            13,  10,  17,  23,  17,  16,   0,   7,
            14,  25,  24,  15,   8,  25,  20,  15,
            19,  20,  11,   6,   7,   6,  20,  16,
            -7,   2, -15, -12, -14, -15, -10, -10),
    'R': (  35,  29,  33,   4,  37,  33,  56,  50,
            55,  29,  56,  67,  55,  62,  34,  60,
            19,  35,  28,  33,  45,  27,  25,  15,
             0,   5,  16,  13,  18,  -4,  -9,  -6,
           -28, -35, -16, -21, -13, -29, -46, -30,
           -42, -28, -42, -25, -25, -35, -26, -46,
           -53, -38, -31, -26, -29, -43, -44, -53,
           -30, -24, -18,   5,  -2, -18, -31, -32),
    'Q': (   6,   1,  -8,-104,  69,  24,  88,  26,
            14,  32,  60, -10,  20,  76,  57,  24,
            -2,  43,  32,  60,  72,  63,  43,   2,
             1, -16,  22,  17,  25,  20, -13,  -6,
           -14, -15,  -2,  -5,  -1, -10, -20, -22,
           -30,  -6, -13, -11, -16, -11, -16, -27,
           -36, -18,   0, -19, -15, -15, -21, -38,
           -39, -30, -31, -13, -31, -36, -34, -42),
    'K': (   4,  54,  47, -99, -99,  60,  83, -62,
           -32,  10,  55,  56,  56,  55,  10,   3,
           -62,  12, -57,  44, -67,  28,  37, -31,
           -55,  50,  11,  -4, -19,  13,   0, -49,
           -55, -43, -52, -28, -51, -47,  -8, -50,
           -47, -42, -43, -79, -64, -32, -29, -32,
            -4,   3, -14, -50, -57, -18,  13,   4,
            17,  30,  -3, -14,   6,  -1,  40,  18),
}

    black_piece_tables = {piece: tuple(flip_table(table)) for piece, table in white_piece_tables.items()}

    score = 0
    for i, piece in enumerate(board):
        if piece != "-":
            if piece[0] == "w":
                score += piece_values[piece[1]]
                score += white_piece_tables[piece[1]][i]
            elif piece[0] == "b":
                score -= piece_values[piece[1]]
                score += black_piece_tables[piece[1]][i]
    return score

def flip_table(table):
    return sum([list(table[i*8:(i+1)*8]) for i in reversed(range(8))], [])

def is_capture(move,board):
    if chess_board[move[1]] != "-":
        return True
    else:
        return False

def get_comp_move(depth):
    best_move = None
    best_score = float('inf')

    for i, piece in enumerate(chess_board):
        if piece != "-" and piece[0] == "b":
            moves = get_moves(i)
            for move in moves:
                temp_board = simulate_move(chess_board, i, move)
                if not check_status(temp_board, "b"):
                    score = evaluate_board(temp_board)
                    if score < best_score:
                        best_score = score
                        best_move = (i, move)

    print("Best Score:", best_score)
    print("Best Move:", best_move)
    return best_move if best_move else (12, 16)  # fallback
    print(best_score)
    print(best_move)
    return best_move

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
        move = get_comp_move(1)
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