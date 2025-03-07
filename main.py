import pygame
import copy
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
    new_board = copy.deepcopy(board)
    piece = new_board[pos]
    target = pos + move

    # Handle en passant
    if piece[-1] == "P" and abs(move) in [7, 9] and new_board[target] == "-":
        if piece[0] == "w" and pos // 8 == 3:
            new_board[target + 8] = "-"
        elif piece[0] == "b" and pos // 8 == 4:
            new_board[target - 8] = "-"

    new_board[target] = piece
    new_board[pos] = "-"
    
    # Handle pawn promotion
    if piece == "wP" and target < 8:
        new_board[target] = "wQ"
    if piece == "bP" and target > 55:
        new_board[target] = "bQ"
    
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
    valid_moves = []
    for move in moves:
        new_board = simulate_move(chess_board, pos, move)
        if not check_status(new_board, piece[0]):
            valid_moves.append(move)
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
    king = color +"K"
    if king not in board:
        return False
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

def generate_moves(board, turn):
    all_moves = []
    for i, piece in enumerate(board):
        if piece != "-" and piece[0] == turn:
            moves = get_moves(i)
            for move in moves:
                temp_board = simulate_move(board, i, move)
                if not check_status(temp_board, turn):
                    all_moves.append((i, move, temp_board))
    return all_moves

# Evaluate the board
# Recursive function given depth that goes through possible moves and whites responses and finds move that gives black best score
# If depth is 0, return the score of the board
def evaluate_board(board, depth, turn):
    piece_values = { "P": 1000, "N": 3000, "B": 3000, "R": 5000, "Q": 9000, "K": 0 }
    if depth == 0:
        score = 0
        for i, piece in enumerate(board):
            if piece != "-":
                value = piece_values.get(piece[1], 0)
                position_bonus = piece_square_bonus(piece, i)  # New
                mobility_bonus = len(get_moves(i)) * 10  # New
                
                if piece[0] == "b":
                    score += value + position_bonus + mobility_bonus
                else:
                    score -= value + position_bonus + mobility_bonus

        print(f"[Depth 0] Evaluated Score: {score}")
        return score
    
    best_score = float("-inf") if turn == "b" else float("inf")
    all_moves = generate_moves(board, turn)

    for _, _, temp_board in all_moves:
        score = evaluate_board(temp_board, depth - 1, "w" if turn == "w" else "b")
        if turn == "b":
            best_score = max(best_score, score)
        else:
            best_score = min(best_score, score)        
    return best_score

def piece_square_bonus(piece, pos):
    # Piece-square tables for strategic play
    tables = {
        "P": [
             0,  0,  0,  0,  0,  0,  0,  0,
           -10, -5, -5,  0,  0, -5, -5, -10,
            -5, -5,  0,  0,  0,  0, -5, -5,
            -5,  0,  0,  5,  5,  0,  0, -5,
             0,  0,  5, 15, 15,  5,  0,  0,
             0,  5, 10, 20, 20, 10,  5,  0,
             5, 10, 15, 25, 25, 15, 10,  5,
             0,  5, 10, 15, 20, 15, 10,  5
        ],
        "N": [
            -50, -40, -30, -30, -30, -30, -40, -50,
            -40, -20,   0,   5,   5,   0, -20, -40,
            -30,   5,  10,  15,  15,  10,   5, -30,
            -30,   0,  15,  20,  20,  15,   0, -30,
            -30,   5,  15,  20,  20,  15,   5, -30,
            -30,   0,  10,  15,  15,  10,   0, -30,
            -40, -20,   0,   0,   0,   0, -20, -40,
            -50, -40, -30, -30, -30, -30, -40, -50
        ],
        "B": [
            -20, -10, -10, -10, -10, -10, -10, -20,
            -10,   0,   5,   0,   0,   5,   0, -10,
            -10,   5,  10,  10,  10,  10,   5, -10,
            -10,   0,  10,  10,  10,  10,   0, -10,
            -10,   5,  10,  10,  10,  10,   5, -10,
            -10,   0,   5,   0,   0,   5,   0, -10,
            -10, -10,   0,   0,   0,   0, -10, -10,
            -20, -10, -10, -10, -10, -10, -10, -20
        ],
        "R": [
             0,   0,   0,   5,   5,   0,   0,   0,
             5,   5,   5,   5,   5,   5,   5,   5,
            -5,   0,   0,   0,   0,   0,   0,  -5,
            -5,   0,   0,   0,   0,   0,   0,  -5,
            -5,   0,   0,   0,   0,   0,   0,  -5,
            -5,   0,   0,   0,   0,   0,   0,  -5,
             0,   0,   5,  10,  10,   5,   0,   0,
             0,   0,   5,  10,  10,   5,   0,   0
        ],
        "Q": [
            -20, -10, -10,  -5,  -5, -10, -10, -20,
            -10,   0,   5,   0,   0,   0,   0, -10,
            -10,   0,   5,   5,   5,   5,   0, -10,
             0,    0,   5,   5,   5,   5,   0,  -5,
             0,    0,   5,   5,   5,   5,   0,  -5,
            -10,   5,   5,   5,   5,   5,   0, -10,
            -10,   0,   0,   0,   0,   0,   0, -10,
            -20, -10, -10,  -5,  -5, -10, -10, -20
        ],
        "K": [
             20,  30,  10,   0,   0,  10,  30,  20,
             20,  20,   0,   0,   0,   0,  20,  20,
            -10, -20, -20, -20, -20, -20, -20, -10,
            -20, -30, -30, -40, -40, -30, -30, -20,
            -30, -40, -40, -50, -50, -40, -40, -30,
            -30, -40, -40, -50, -50, -40, -40, -30,
            -30, -40, -40, -50, -50, -40, -40, -30,
            -30, -40, -40, -50, -50, -40, -40, -30
        ]
    }
    
    # Extract piece type and color
    color, piece_type = piece[0], piece[1]
    
    if piece_type in tables:
        # Black should see the board from their perspective (flipped)
        if color == "b":
            return -tables[piece_type][pos]
        else:
            return tables[piece_type][63 - pos]  # Flip for White
            
    return 0  # Default return for unknown pieces

            

def get_comp_move():
    best_move = None
    best_score =  float("-inf")
    depth = 2

    all_moves = generate_moves(chess_board, "b")

    for i, move, temp_board in all_moves:
        score = evaluate_board(temp_board, depth - 1, "w")
        print(f"Move {i} -> {move} has score {score}")
        if score > best_score:
            best_score = score
            best_move = (i, move)
    

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
        comp_move = get_comp_move()
        if comp_move:
            move_piece(comp_move[0], comp_move[1])
            turn = "w"
        else:
            print("No valid moves for black")
            running = False
        
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