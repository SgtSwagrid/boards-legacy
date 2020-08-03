from .common.game import *
from .common.handler import *


class Amazons(Game):
    name = "Amazons"
    id = 6
    width = 8
    height = 8
    players = 2

    class AmazonPiece(PieceType):
        id = 0

        # White is player 1, black player 2
        def texture(self, owner):
            if owner == 0:
                return 'games/img/chess/white_queen.png'
            else:
                return 'games/img/chess/black_queen.png'

        def move_valid(self, state, piece, x_to, y_to):
            return state.turn.stage == 0 and \
                not state.pieces[x_to][y_to] and \
                state.game.is_queen_move(state, piece, x_to, y_to)

        def move_piece(self, state, piece, x_to, y_to):
            return state \
                .move_piece(piece, x_to, y_to) \
                .end_stage()

    class ArrowPiece(PieceType):
        id = 1

        def texture(self, owner):
            if owner == 0:
                return 'games/img/chess/white_pawn.png'
            else:
                return 'games/img/chess/black_pawn.png'

        def place_valid(self, state, piece):
            if len(state.changes) == 0: return False
            x_from, y_from = state.changes[-1]

            queen = Piece(self, state.turn.current, x_from, y_from)

            return state.turn.stage == 1 and \
                not state.pieces[piece.x][piece.y] and \
                state.game.is_queen_move(state, queen, piece.x, piece.y)

        def place_piece(self, state, piece):
            piece = Piece(self, state.turn.current, piece.x, piece.y)
            state_next_turn = state.place_piece(piece).end_turn()

            return state_next_turn if state.game.can_move(state_next_turn) \
                else state_next_turn.end_game(winner=state.turn.current)

    types = [AmazonPiece(), ArrowPiece()]
    handlers = [MoveHandler(), PlaceHandler(ArrowPiece())]

    def piece(self, x, y):
        # Top and bottom arrangement

        tw = self.width // 3
        th = self.height // 3

        op_tw = self.width - 1 - tw
        op_th = self.height - 1 - th

        white_queens = [[tw, 0], [op_tw, 0], [0, th], [self.width-1, th]]
        black_queens = [[tw, self.height-1], [op_tw, self.height-1], [0, op_th], [self.width-1, op_th]]

        if [x, y] in white_queens:
            return Piece(self.AmazonPiece(), 0, x, y)  # White

        if [x, y] in black_queens:
            return Piece(self.AmazonPiece(), 1, x, y)  # White

        return None

    def can_move(self, state):
        return any([state.open(piece.x + dx, piece.y + dy)
                    for dx in range(-1, 2)
                    for dy in range(-1, 2)
                    for piece in state.pieces_by_player[state.turn.current]
                    if piece.type.id == self.AmazonPiece().id])

    def is_queen_move(self, state, piece, x_to, y_to):
        dx, dy = delta(piece.x, piece.y, x_to, y_to)
        sx, sy = direction(piece.x, piece.y, x_to, y_to)
        d = distance(piece.x, piece.y, x_to, y_to)
        return (((sx == 0) ^ (sy == 0)) or (abs(dx) == abs(dy))) and \
               path(piece.x, piece.y, sx, sy, d, state.pieces)

def distance(x_from, y_from, x_to, y_to):
    return max(abs(x_to - x_from), abs(y_to - y_from))


def delta(x_from, y_from, x_to, y_to):
    return abs(x_to - x_from), abs(y_to - y_from)


def direction(x_from, y_from, x_to, y_to):
    return (-1 if x_to < x_from else 0 if x_to == x_from else 1), \
            (-1 if y_to < y_from else 0 if y_to == y_from else 1)

def path(x, y, sx, sy, d, pieces):
    return all(map(lambda r: not pieces
    [x + sx * r][y + sy * r], range(1, d)))