import asyncio
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
START_BOARD = chess_board.copy()  # used to reset the board for "play again"

# Draw chess board
def draw_chess_board():
    for i in range(8):
        for j in range(8):
            if (i+j) % 2 == 0:
                pygame.draw.rect(screen, light_purple, (i*100+100, j*100+100, 100, 100))
            else:
                pygame.draw.rect(screen, dark_purple, (i*100+100, j*100+100, 100, 100))

#Draw piece
piece_images = {}

def draw_piece(piece, pos):
    # Load each image once and reuse it; reloading from disk every frame causes flicker
    if piece not in piece_images:
        # image files are lowercase (e.g. "bk.png"); the web is case-sensitive
        data = pygame.image.load("images/" + piece.lower() + ".png")
        piece_images[piece] = pygame.transform.scale(data, (100, 100))
    screen.blit(piece_images[piece], (pos))

# Loop through the chess board and draw the pieces
def refresh_pieces(exclude=None):
    for index, piece in enumerate(chess_board):
        if piece != "-" and index != exclude:
            row = index // 8
            col = index % 8
            draw_piece(piece, (col * 100 + 100, row * 100 + 100))

last_move = None

# Castling rights: [white king-side, white queen-side, black king-side, black queen-side]
castling_rights = [True, True, True, True]
# Moving from (or capturing on) one of these squares removes the listed castling rights
CASTLE_MASK = {60: (0, 1), 63: (0,), 56: (1,), 4: (2, 3), 7: (2,), 0: (3,)}

# Move piece
def move_piece(pos, move):
    global last_move
    piece = chess_board[pos]
    target = pos + move
    for square in (pos, target):
        for i in CASTLE_MASK.get(square, ()):
            castling_rights[i] = False
    if piece[-1] != "P":
        last_move = None  # en passant is only possible right after the two-square pawn move
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
            # the captured pawn sits directly behind the target square
            if piece[0] == "w":
                chess_board[target + 8] = "-"
            else:
                chess_board[target - 8] = "-"
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
        if piece[-1] == "K" and abs(move) == 2:
            # Castling: the king may not castle out of check or through an attacked square
            if check_status(chess_board, piece[0]) or \
                    check_status(simulate_move(chess_board, pos, move // 2), piece[0]):
                continue
        new_board = simulate_move(chess_board, pos, move)
        if piece[-1] == "P" and abs(move) in (7, 9) and chess_board[pos + move] == "-":
            # En passant: the captured pawn is beside the moving pawn, not on the target square
            new_board[pos + move + (8 if piece[0] == "w" else -8)] = "-"
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

    # En passant: capture an enemy pawn that just moved two squares to land beside this pawn
    if last_move is not None:
        ep_from, ep_to = last_move
        if board[ep_to] != "-" and board[ep_to][1] == "P" and board[ep_to][0] != color \
                and ep_to // 8 == pos // 8 and abs(ep_to % 8 - pos % 8) == 1:
            moves.append((ep_from + ep_to) // 2 - pos)

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
    team_color = board[pos][0]  # 'w' for white, 'b' for black

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

def get_king_moves(pos, board, include_castling=True):
    moves = []
    king_color = board[pos][0]
    # Castling is only allowed if neither the king nor that rook has moved yet
    # (checks for castling out of / through check are done in get_moves)
    if include_castling and king_color == "w":
        if pos == 60:
            if castling_rights[0] and board[61] == "-" and board[62] == "-" and board[63] == "wR":
                moves.append(2)
            if castling_rights[1] and board[59] == "-" and board[58] == "-" and board[57] == "-" and board[56] == "wR":
                moves.append(-2)
    elif include_castling and king_color == "b":
        if pos == 4:
            if castling_rights[2] and board[5] == "-" and board[6] == "-" and board[7] == "bR":
                moves.append(2)
            if castling_rights[3] and board[3] == "-" and board[2] == "-" and board[1] == "-" and board[0] == "bR":
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
                moves = get_king_moves(i, board, include_castling=False)  # castling never attacks
            for move in moves:
                squares.append(i + move)
    return squares

def check_status(board, color):
    king_pos = board.index(color + "K")
    opponent = "b" if color == "w" else "w"
    return king_pos in danger_squares(board,opponent)

def has_legal_moves(color):
    # get_moves already removes moves that leave the king in check
    for i, piece in enumerate(chess_board):
        if piece != "-" and piece[0] == color and get_moves(i):
            return True
    return False

def checkmate(color):
    # No legal moves AND in check
    return not has_legal_moves(color) and check_status(chess_board, color)

def stalemate(color):
    # No legal moves but NOT in check: the game is a draw
    return not has_legal_moves(color) and not check_status(chess_board, color)

# =====================================================================
# Computer player (black) - negamax alpha-beta search
# =====================================================================
# Everything below works on its own copy of the board, never on the global
# chess_board, so the search really looks ahead. Scores are from White's
# point of view in evaluate_board() and flipped to the side to move inside
# the search (negamax).
import time

AI_TIME_LIMIT = 3.0     # seconds the computer may think per move
AI_MAX_DEPTH = 64       # iterative deepening stops on time long before this

PIECE_VALUES = {"P": 100, "N": 280, "B": 320, "R": 479, "Q": 929, "K": 0}
MATE_SCORE = 100000
INF = 10 ** 9

def flip_table(table):
    return sum([list(table[i*8:(i+1)*8]) for i in reversed(range(8))], [])

# Piece-square tables from White's point of view (index 0 = a8)
WHITE_PST = {
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
# In the endgame the king should walk to the centre instead of hiding
KING_ENDGAME_PST = (
    -50, -30, -30, -30, -30, -30, -30, -50,
    -30, -20, -10,   0,   0, -10, -20, -30,
    -30, -10,  20,  30,  30,  20, -10, -30,
    -30, -10,  30,  40,  40,  30, -10, -30,
    -30, -10,  30,  40,  40,  30, -10, -30,
    -30, -10,  20,  30,  30,  20, -10, -30,
    -30, -30,   0,   0,   0,   0, -30, -30,
    -50, -30, -30, -30, -30, -30, -30, -50)
BLACK_PST = {p: tuple(flip_table(t)) for p, t in WHITE_PST.items()}
WHITE_KING_END = KING_ENDGAME_PST
BLACK_KING_END = tuple(flip_table(KING_ENDGAME_PST))
START_NON_PAWN = 2 * (2 * 280 + 2 * 320 + 2 * 479 + 929)

# ---- precomputed board geometry (avoids wrap-around bugs at the edges) ----
def _build_geometry():
    knight, king, rook_rays, bishop_rays = [], [], [], []
    for sq in range(64):
        r, c = divmod(sq, 8)
        knight.append([(r + dr) * 8 + c + dc for dr, dc in
                       ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
                       if 0 <= r + dr < 8 and 0 <= c + dc < 8])
        king.append([(r + dr) * 8 + c + dc for dr in (-1, 0, 1) for dc in (-1, 0, 1)
                     if (dr or dc) and 0 <= r + dr < 8 and 0 <= c + dc < 8])
        def rays(dirs):
            out = []
            for dr, dc in dirs:
                ray, rr, cc = [], r + dr, c + dc
                while 0 <= rr < 8 and 0 <= cc < 8:
                    ray.append(rr * 8 + cc)
                    rr += dr
                    cc += dc
                if ray:
                    out.append(ray)
            return out
        rook_rays.append(rays(((-1, 0), (1, 0), (0, -1), (0, 1))))
        bishop_rays.append(rays(((-1, -1), (-1, 1), (1, -1), (1, 1))))
    return knight, king, rook_rays, bishop_rays

KNIGHT_TARGETS, KING_TARGETS, ROOK_RAYS, BISHOP_RAYS = _build_geometry()

# Search state tuple: (white K-side, white Q-side, black K-side, black Q-side, en passant square)
# CASTLE_MASK is defined next to move_piece
NO_RIGHTS = (False, False, False, False, None)


def is_attacked(board, sq, by):
    """True if square sq is attacked by any piece of colour `by`."""
    r, c = divmod(sq, 8)
    if by == "w":
        pr, pawn = r + 1, "wP"
    else:
        pr, pawn = r - 1, "bP"
    if 0 <= pr < 8:
        if c > 0 and board[pr * 8 + c - 1] == pawn:
            return True
        if c < 7 and board[pr * 8 + c + 1] == pawn:
            return True
    knight = by + "N"
    for t in KNIGHT_TARGETS[sq]:
        if board[t] == knight:
            return True
    king = by + "K"
    for t in KING_TARGETS[sq]:
        if board[t] == king:
            return True
    rook, bishop, queen = by + "R", by + "B", by + "Q"
    for ray in ROOK_RAYS[sq]:
        for t in ray:
            p = board[t]
            if p != "-":
                if p == rook or p == queen:
                    return True
                break
    for ray in BISHOP_RAYS[sq]:
        for t in ray:
            p = board[t]
            if p != "-":
                if p == bishop or p == queen:
                    return True
                break
    return False


def gen_moves(board, color, rights, captures_only=False):
    """Pseudo-legal moves as (from, to) pairs. Legality (king safety) is checked by the caller."""
    moves = []
    enemy = "b" if color == "w" else "w"
    for sq in range(64):
        p = board[sq]
        if p == "-" or p[0] != color:
            continue
        kind = p[1]
        if kind == "P":
            r, c = divmod(sq, 8)
            step = -8 if color == "w" else 8
            fwd = sq + step
            for dc in (-1, 1):
                if 0 <= c + dc < 8:
                    t = fwd + dc
                    if board[t] != "-" and board[t][0] == enemy:
                        moves.append((sq, t))
            ep = rights[4]
            if ep is not None and ep // 8 == fwd // 8 and abs(ep % 8 - c) == 1:
                moves.append((sq, ep))      # en passant capture
            if board[fwd] == "-":
                promo = (color == "w" and r == 1) or (color == "b" and r == 6)
                if promo or not captures_only:
                    moves.append((sq, fwd))
                if not captures_only and r == (6 if color == "w" else 1) and board[fwd + step] == "-":
                    moves.append((sq, fwd + step))
        elif kind == "N" or kind == "K":
            for t in (KNIGHT_TARGETS[sq] if kind == "N" else KING_TARGETS[sq]):
                q = board[t]
                if q == "-":
                    if not captures_only:
                        moves.append((sq, t))
                elif q[0] == enemy:
                    moves.append((sq, t))
            if kind == "K" and not captures_only:
                _add_castling(board, color, sq, rights, moves)
        else:
            if kind == "R":
                ray_sets = (ROOK_RAYS[sq],)
            elif kind == "B":
                ray_sets = (BISHOP_RAYS[sq],)
            else:
                ray_sets = (ROOK_RAYS[sq], BISHOP_RAYS[sq])
            for rays in ray_sets:
                for ray in rays:
                    for t in ray:
                        q = board[t]
                        if q == "-":
                            if not captures_only:
                                moves.append((sq, t))
                        else:
                            if q[0] == enemy:
                                moves.append((sq, t))
                            break
    return moves


def _add_castling(board, color, sq, rights, moves):
    if color == "w" and sq == 60:
        if rights[0] and board[61] == "-" and board[62] == "-" and board[63] == "wR" \
                and not any(is_attacked(board, s, "b") for s in (60, 61, 62)):
            moves.append((60, 62))
        if rights[1] and board[59] == "-" and board[58] == "-" and board[57] == "-" and board[56] == "wR" \
                and not any(is_attacked(board, s, "b") for s in (60, 59, 58)):
            moves.append((60, 58))
    elif color == "b" and sq == 4:
        if rights[2] and board[5] == "-" and board[6] == "-" and board[7] == "bR" \
                and not any(is_attacked(board, s, "w") for s in (4, 5, 6)):
            moves.append((4, 6))
        if rights[3] and board[3] == "-" and board[2] == "-" and board[1] == "-" and board[0] == "bR" \
                and not any(is_attacked(board, s, "w") for s in (4, 3, 2)):
            moves.append((4, 2))


def ep_square(board, frm, to):
    """After a pawn moves frm->to, the en passant target square if an enemy pawn can use it."""
    piece = board[to]
    if piece[1] != "P" or abs(to - frm) != 16:
        return None
    enemy_pawn = ("b" if piece[0] == "w" else "w") + "P"
    c = to % 8
    if (c > 0 and board[to - 1] == enemy_pawn) or (c < 7 and board[to + 1] == enemy_pawn):
        return (frm + to) // 2
    return None


def make_move(board, frm, to, rights):
    """Return (new_board, new_state) after the move; handles castling, en passant and promotion.
    state = (white K-side, white Q-side, black K-side, black Q-side, en passant square or None)"""
    b = board[:]
    p = b[frm]
    b[to] = p
    b[frm] = "-"
    if p[1] == "P" and to == rights[4]:
        b[to + 8 if p[0] == "w" else to - 8] = "-"   # remove the pawn taken en passant
    new_ep = ep_square(b, frm, to) if p[1] == "P" else None
    if new_ep != rights[4]:
        rights = rights[:4] + (new_ep,)
    if p[1] == "K" and abs(to - frm) == 2:
        if to > frm:
            b[frm + 1] = b[frm + 3]
            b[frm + 3] = "-"
        else:
            b[frm - 1] = b[frm - 4]
            b[frm - 4] = "-"
    elif p == "wP" and to < 8:
        b[to] = "wQ"
    elif p == "bP" and to > 55:
        b[to] = "bQ"
    if frm in CASTLE_MASK or to in CASTLE_MASK:
        r = list(rights)
        for s in (frm, to):
            for i in CASTLE_MASK.get(s, ()):
                r[i] = False
        rights = tuple(r)
    return b, rights


def evaluate_board(board):
    """Static evaluation from White's point of view (positive = good for White)."""
    score = 0
    non_pawn = 0
    wk = bk = -1
    w_bishops = b_bishops = 0
    for sq, p in enumerate(board):
        if p == "-":
            continue
        kind = p[1]
        if p[0] == "w":
            if kind == "K":
                wk = sq
                continue
            score += PIECE_VALUES[kind] + WHITE_PST[kind][sq]
            if kind == "B":
                w_bishops += 1
        else:
            if kind == "K":
                bk = sq
                continue
            score -= PIECE_VALUES[kind] + BLACK_PST[kind][sq]
            if kind == "B":
                b_bishops += 1
        if kind != "P":
            non_pawn += PIECE_VALUES[kind]

    if w_bishops >= 2:
        score += 30
    if b_bishops >= 2:
        score -= 30

    # Blend king tables between middlegame and endgame
    phase = min(non_pawn, START_NON_PAWN) / START_NON_PAWN
    if wk >= 0:
        score += phase * WHITE_PST["K"][wk] + (1 - phase) * WHITE_KING_END[wk]
    if bk >= 0:
        score -= phase * BLACK_PST["K"][bk] + (1 - phase) * BLACK_KING_END[bk]

    # Mop-up: when clearly winning in an endgame, drive the enemy king to the edge
    if phase < 0.35 and abs(score) > 300 and wk >= 0 and bk >= 0:
        loser = bk if score > 0 else wk
        lr, lc = divmod(loser, 8)
        center_dist = max(3 - lr, lr - 4) + max(3 - lc, lc - 4)
        wr, wc = divmod(wk, 8)
        br, bc = divmod(bk, 8)
        king_dist = abs(wr - br) + abs(wc - bc)
        bonus = 10 * center_dist + 4 * (14 - king_dist)
        score += bonus if score > 0 else -bonus
    return int(score)


class _SearchTimeout(Exception):
    pass


EXACT, LOWER, UPPER = 0, 1, 2


class Searcher:
    def __init__(self, history, time_limit):
        self.history = history          # positions that already occurred in the game
        self.path = []                  # positions on the current search line
        self.tt = {}                    # transposition table
        self.killers = {}
        self.nodes = 0
        self.deadline = time.time() + time_limit
        self.start = time.time()
        self.time_limit = time_limit

    def _tick(self):
        self.nodes += 1
        if self.nodes & 1023 == 0:
            pygame.event.pump()         # keep the window responsive while thinking
            if time.time() > self.deadline:
                raise _SearchTimeout()

    def _order(self, board, moves, tt_move, ply, color):
        pst = WHITE_PST if color == "w" else BLACK_PST
        killers = self.killers.get(ply, ())

        def key(m):
            frm, to = m
            if m == tt_move:
                return 10 ** 7
            mover = board[frm][1]
            victim = board[to]
            s = 0
            if victim != "-":
                s = 10 ** 6 + 10 * PIECE_VALUES[victim[1]] - PIECE_VALUES[mover]
            elif m in killers:
                s = 5 * 10 ** 5
            if mover == "P" and (to < 8 or to > 55):
                s += 9 * 10 ** 5
            if mover != "K":
                s += pst[mover][to] - pst[mover][frm]
            return s
        return sorted(moves, key=key, reverse=True)

    def quiesce(self, board, color, alpha, beta, ply):
        self._tick()
        stand = evaluate_board(board)
        if color == "b":
            stand = -stand
        if stand >= beta:
            return stand
        if stand > alpha:
            alpha = stand
        enemy = "b" if color == "w" else "w"
        king_sq = board.index(color + "K")
        for frm, to in self._order(board, gen_moves(board, color, NO_RIGHTS, True), None, ply, color):
            victim = board[to]
            # delta pruning: skip captures that cannot possibly raise alpha
            if victim != "-" and stand + PIECE_VALUES[victim[1]] + 200 < alpha:
                continue
            nb, _ = make_move(board, frm, to, NO_RIGHTS)
            if is_attacked(nb, to if frm == king_sq else king_sq, enemy):
                continue
            score = -self.quiesce(nb, enemy, -beta, -alpha, ply + 1)
            if score >= beta:
                return score
            if score > alpha:
                alpha = score
        return alpha

    def negamax(self, board, color, rights, depth, alpha, beta, ply):
        self._tick()
        key = (tuple(board), color, rights)
        if key in self.path or key in self.history:
            return 0                    # repetition = draw
        enemy = "b" if color == "w" else "w"
        king_sq = board.index(color + "K")
        in_check = is_attacked(board, king_sq, enemy)
        if in_check:
            depth += 1                  # check extension
        if depth <= 0:
            return self.quiesce(board, color, alpha, beta, ply)

        tt_move = None
        entry = self.tt.get(key)
        if entry:
            t_depth, t_score, t_flag, tt_move = entry
            if t_depth >= depth:
                if t_score > MATE_SCORE - 1000:
                    t_score -= ply
                elif t_score < -MATE_SCORE + 1000:
                    t_score += ply
                if t_flag == EXACT:
                    return t_score
                if t_flag == LOWER and t_score >= beta:
                    return t_score
                if t_flag == UPPER and t_score <= alpha:
                    return t_score

        alpha_orig = alpha
        best, best_move, legal = -INF, None, 0
        self.path.append(key)
        try:
            for move in self._order(board, gen_moves(board, color, rights), tt_move, ply, color):
                frm, to = move
                nb, nr = make_move(board, frm, to, rights)
                if is_attacked(nb, to if frm == king_sq else king_sq, enemy):
                    continue
                legal += 1
                score = -self.negamax(nb, enemy, nr, depth - 1, -beta, -alpha, ply + 1)
                if score > best:
                    best, best_move = score, move
                if score > alpha:
                    alpha = score
                if alpha >= beta:
                    if board[to] == "-":
                        k = self.killers.setdefault(ply, [])
                        if move not in k:
                            k.insert(0, move)
                            del k[2:]
                    break
        finally:
            self.path.pop()

        if legal == 0:
            return -MATE_SCORE + ply if in_check else 0   # checkmate or stalemate

        stored = best
        if stored > MATE_SCORE - 1000:
            stored += ply
        elif stored < -MATE_SCORE + 1000:
            stored -= ply
        flag = UPPER if best <= alpha_orig else LOWER if best >= beta else EXACT
        self.tt[key] = (depth, stored, flag, best_move)
        return best

    def search(self, board, color, rights, max_depth):
        enemy = "b" if color == "w" else "w"
        king_sq = board.index(color + "K")
        root_moves = []
        for frm, to in gen_moves(board, color, rights):
            nb, nr = make_move(board, frm, to, rights)
            if not is_attacked(nb, to if frm == king_sq else king_sq, enemy):
                root_moves.append(((frm, to), nb, nr))
        if not root_moves:
            return None, 0
        if len(root_moves) == 1:
            return root_moves[0][0], 0

        order = self._order(board, [m for m, _, _ in root_moves], None, 0, color)
        lookup = {m: (nb, nr) for m, nb, nr in root_moves}
        best_move, best_score = order[0], -INF
        root_key = (tuple(board), color, rights)

        for depth in range(1, max_depth + 1):
            cur_best, cur_score = None, -INF
            alpha, beta = -INF, INF
            scores = {}
            self.path.append(root_key)
            try:
                for move in order:
                    nb, nr = lookup[move]
                    score = -self.negamax(nb, enemy, nr, depth - 1, -beta, -alpha, 1)
                    scores[move] = score
                    if score > cur_score:
                        cur_best, cur_score = move, score
                    if score > alpha:
                        alpha = score
            except _SearchTimeout:
                # The previous best move is searched first, so a partial result is still safe
                if cur_best is not None:
                    best_move, best_score = cur_best, cur_score
                break
            finally:
                self.path.pop()
            best_move, best_score = cur_best, cur_score
            print(f"depth {depth}: best {best_move} score {best_score} nodes {self.nodes}")
            order.sort(key=lambda m: scores.get(m, -INF), reverse=True)
            if abs(best_score) > MATE_SCORE - 1000:
                break                   # forced mate found
            if time.time() - self.start > self.time_limit * 0.5:
                break                   # next depth would not finish in time
        return best_move, best_score


# Game positions seen so far (used to avoid repeating moves)
game_history = set()


def get_comp_move(depth=3, max_depth=5, force_capture=True):
    """Pick the computer's (black) move. Returns (start_pos, offset) like the player moves.
    The arguments are kept for compatibility; thinking time is set by AI_TIME_LIMIT."""
    ep = ep_square(chess_board, *last_move) if last_move else None
    rights = tuple(castling_rights) + (ep,)
    board = chess_board[:]
    root_key = (tuple(board), "b", rights)
    searcher = Searcher(game_history, AI_TIME_LIMIT)
    move, score = searcher.search(board, "b", rights, AI_MAX_DEPTH)
    game_history.add(root_key)
    if move is None:
        return None
    frm, to = move
    nb, nr = make_move(board, frm, to, rights)
    game_history.add((tuple(nb), "w", nr))
    print(f"Computer plays {chess_board[frm]} {frm} -> {to}  (eval {score}, {searcher.nodes} nodes, "
          f"{time.time() - searcher.start:.2f}s)")
    return (frm, to - frm)

# Game loop
running = True
selected_piece = None
dragging = False
turn = "w"
game_over = False   # when True the final position stays on screen until the window is closed
frames_before_ai = 2  # frames to display the player's move before the computer starts thinking
clock = pygame.time.Clock()

def on_board(mouse_pos):
    x, y = mouse_pos
    return 100 <= x < 900 and 100 <= y < 900

game_result = ""     # message shown on the game-over banner

def game_finished(side_to_move):
    # Called after every move with the side whose turn it now is
    global game_result
    if checkmate(side_to_move):
        game_result = "Checkmate - " + ("Black wins" if side_to_move == "w" else "White wins")
    elif stalemate(side_to_move):
        game_result = "Stalemate - Draw"
    else:
        return False
    print(game_result)
    return True

banner_fonts = None

def draw_game_over(message):
    # Plain box over the middle of the board using the board colours and pygame's default font
    global banner_fonts
    if banner_fonts is None:
        pygame.font.init()
        banner_fonts = (pygame.font.Font(None, 56), pygame.font.Font(None, 36))
    box = pygame.Rect(200, 400, 600, 200)
    pygame.draw.rect(screen, light_purple, box)
    pygame.draw.rect(screen, dark_purple, box, 4)
    for font, text, y in ((banner_fonts[0], message, 470), (banner_fonts[1], "Click to play again", 540)):
        surface = font.render(text, True, black)
        screen.blit(surface, surface.get_rect(center=(500, y)))

def reset_game():
    global last_move, turn, game_over, game_result, frames_before_ai, selected_piece, dragging
    chess_board[:] = START_BOARD
    castling_rights[:] = [True, True, True, True]
    game_history.clear()
    last_move = None
    turn = "w"
    game_over = False
    game_result = ""
    frames_before_ai = 2
    selected_piece = None
    dragging = False

async def main():
    # async so the game can also run in a web browser (pygbag); await hands control
    # back to the browser once per frame. Runs exactly the same on the desktop.
    global running, selected_piece, dragging, turn, game_over, frames_before_ai, game_result
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and game_over:
                reset_game()  # click anywhere on the game-over banner screen to play again
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if on_board(mouse_pos):
                    pos = get_board_pos(mouse_pos)
                    if chess_board[pos] != "-":
                        selected_piece = pos
                        dragging = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if dragging:
                    mouse_pos = pygame.mouse.get_pos()
                    if on_board(mouse_pos):
                        new_pos = get_board_pos(mouse_pos)
                        move = new_pos - selected_piece
                        if chess_board[selected_piece][0] == turn and move in get_moves(selected_piece):
                            move_piece(selected_piece, move)
                            turn = "b" if turn == "w" else "w"
                            if game_finished(turn):
                                game_over = True
                    dragging = False
                    selected_piece = None

        # Draw everything once per frame; the dragged piece is drawn last so it stays on top
        screen.fill(black)
        draw_chess_board()
        refresh_pieces(selected_piece if dragging else None)
        if dragging:
            mouse_pos = pygame.mouse.get_pos()
            draw_piece(chess_board[selected_piece], (mouse_pos[0] - 50, mouse_pos[1] - 50))
        if game_over:
            draw_game_over(game_result)
        pygame.display.update()

        # The computer moves only after the player's move has actually appeared on screen.
        # In a browser the screen is only painted when we hand control back (await below),
        # so first show a couple of frames with the player's move, then start thinking.
        if running and not game_over and turn == "b" and frames_before_ai > 0:
            frames_before_ai -= 1
        elif running and not game_over and turn == "b":
            frames_before_ai = 2
            move = get_comp_move(3, max_depth=5, force_capture=True)
            if move:
                move_piece(move[0], move[1])
                turn = "w"
                if game_finished(turn):
                    game_over = True
            else:
                print("No valid moves found for black")
                game_result = "Game over"
                game_over = True

        clock.tick(60)
        await asyncio.sleep(0)

    pygame.quit()

asyncio.run(main())
