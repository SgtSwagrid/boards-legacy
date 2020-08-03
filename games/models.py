from django.db import models
from django.contrib.auth.models import User

from games.games.common.action import *
from games.games.common.games import games
from datetime import time
import random

from .games.common.game import *
from .games.common.state import *

class BoardManager(models.Manager):

    def create(self, game):

        code = hex(random.randint(0, 1048575))[2:].zfill(5).upper()
        state = StateModel.states.create(game.setup(), previous=None)
        board = super().create(game_id=game.id, code=code, state=state)
        return board

class BoardModel(models.Model):

    boards = BoardManager()

    game_id = models.IntegerField()

    code = models.CharField(max_length=5)

    state = models.ForeignKey('StateModel',
        on_delete=models.SET_NULL, null=True, blank=True)

    status = models.IntegerField(default=0)

    time = models.DateTimeField(auto_now_add=True)

    class Meta: ordering = ['-time']

    def __str__(self): return self.code + " " + self.game().name

    def set_state(self, state):
        self.state = StateModel.states.create(state, previous=self.state)
        if self.state.outcome != -2: self.status = 2
        self.save()

    def current(self, player):
        return player and player.order == self.state.current

    def players(self):
        return PlayerModel.objects.filter(board=self)

    def player(self, user):
        return self.players().filter(user=user).first()\
            if user.is_authenticated else None

    def game(self):
        return games[self.game_id]

    def winner(self):
        return self.players()[self.state.outcome]\
            if self.state.outcome > -1 else None

    def join(self, user):
        order = self.players().count()
        PlayerModel.objects.create(user=user, board=self,
            order=order, leader=order == 0)

    def start(self):
        self.status = 1
        self.save()

class PlayerModel(models.Model):

    user = models.ForeignKey(User,
        on_delete=models.SET_NULL, null=True)

    board = models.ForeignKey(BoardModel, on_delete=models.CASCADE)

    order = models.IntegerField()

    score = models.IntegerField(default=0)

    leader = models.BooleanField(default=False)

    time = models.TimeField(default=time(0, 0, 0))

    forfeited = models.BooleanField(default=False)

    class Meta: ordering = ['board', 'order']

    def __str__(self): return self.board.code + " " + self.user.username

    def leave(self):

        for player in self.board.players().filter(order__gt=self.order):
            player.order -= 1
            player.save()
        self.delete()

        if self.leader:
            other_player = self.board.players().first()
            if other_player:
                other_player.leader = True
                other_player.save()
            else:
                self.board.delete()

    def promote(self):

        other_player = self.board.players().get(order=self.order-1)
        other_player.order += 1
        other_player.save()
        self.order -= 1
        self.save()

    def demote(self):

        other_player = self.board.players().get(order=self.order+1)
        other_player.order -= 1
        other_player.save()
        self.order += 1
        self.save()

    def transfer(self):

        other_player = self.board.players().get(leader=True)
        other_player.leader = False
        other_player.save()
        self.leader = True
        self.save()

    def forfeit(self):

        self.forfeited = True
        self.save()
        remaining = self.board.players().filter(forfeited=False)
        if len(remaining) == 1:
            self.board.state.outcome = remaining.get().order
            self.board.state.save()
            self.board.status = 2
            self.board.save()

class StateManager(models.Manager):

    def create(self, state, previous):

        action = ActionModel.actions.create(state.action)\
            if state.action else None

        state_model = super().create(
            game_id=state.game.id,
            action=action,
            current=state.turn.current,
            stage=state.turn.stage,
            ply=state.turn.ply,
            epoch=state.turn.epoch,
            outcome=-2 if not state.outcome.finished else
                -1 if state.outcome.draw else
                state.outcome.winner,
            previous=previous)

        for player in state.players:
            PlayerStateModel.players.create(player, state_model)

        for col in state.pieces:
            for piece in col:
                if piece: PieceModel.pieces.create(piece, state_model)

        return state_model

class StateModel(models.Model):

    states = StateManager()

    game_id = models.IntegerField()

    action = models.ForeignKey('ActionModel',
        on_delete=models.CASCADE, null=True)

    current = models.IntegerField(default=0)

    stage = models.IntegerField(default=0)

    ply = models.IntegerField(default=0)

    epoch = models.IntegerField(default=0)

    outcome = models.IntegerField(default=-2)

    previous = models.ForeignKey('StateModel',
        on_delete=models.CASCADE, null=True)

    def get_players(self):

        return [p.get_player() for p in
            PlayerStateModel.players.filter(state=self)]

    def get_pieces(self):

        def to_piece(piece): return piece.get_piece() if piece else None
        game = games[self.game_id]

        return [[to_piece(PieceModel.pieces
            .filter(state=self, x=x, y=y).first())
            for y in range(0, game.height)]
            for x in range(0, game.width)]

    def get_action(self):
        return self.action.get_action(self) if self.action else None

    def get_turn(self):

        return Turn(
            current=self.current,
            stage=self.stage,
            ply=self.ply,
            epoch=self.epoch)

    def get_outcome(self):

        return Outcome(
            finished=self.outcome > -2,
            winner=self.outcome,
            draw=self.outcome == -1)

    def get_state(self):

        return State(
            game=games[self.game_id],
            players=self.get_players(),
            pieces=self.get_pieces(),
            action=self.get_action(),
            turn=self.get_turn(),
            outcome=self.get_outcome(),
            previous=self.get_previous_state)

    def get_previous_state(self):
        return self.previous.get_state() if self.previous else None

class PlayerStateManager(models.Manager):

    def create(self, player, state):

        return super().create(
            state=state,
            order=player.order,
            score=player.score,
            mode=player.mode)

class PlayerStateModel(models.Model):

    players = PlayerStateManager()

    state = models.ForeignKey(StateModel, on_delete=models.CASCADE)

    order = models.IntegerField()

    score = models.IntegerField(default=0)

    mode = models.IntegerField(default=0)

    class Meta: ordering = ['state', 'order']

    def get_player(self):

        return PlayerState(
            order=self.order,
            score=self.score,
            mode=self.mode)

class PieceManager(models.Manager):

    def create(self, piece, state):

        return super().create(
            state=state,
            type=piece.type.id,
            owner=piece.owner,
            x=piece.x,
            y=piece.y,
            mode=piece.mode)

class PieceModel(models.Model):

    pieces = PieceManager()

    state = models.ForeignKey(StateModel, on_delete=models.CASCADE)

    type = models.IntegerField()

    owner = models.IntegerField()

    x = models.IntegerField()

    y = models.IntegerField()

    mode = models.IntegerField(default=0)

    class Meta: ordering = ['state']

    def get_piece(self):

        return Piece(
            type=games[self.state.game_id].types[self.type],
            owner=self.owner,
            x=self.x,
            y=self.y,
            mode=self.mode)

class ActionManager(models.Manager):

    def create(self, action):

        if isinstance(action, PlaceAction):
            action_model = super().create(type=0,
                x_to=action.piece.x,
                y_to=action.piece.y)

        elif isinstance(action, MoveAction):
            action_model = super().create(type=1,
                x_from=action.piece.x,
                y_from=action.piece.y,
                x_to=action.x_to,
                y_to=action.y_to)

        elif isinstance(action, RemoveAction):
            action_model = super().create(type=1,
                x_from=action.piece.x,
                y_from=action.piece.y)

        for change in action.changes:
            ChangeModel.objects.create(action=action_model, x=change[0], y=change[1])

        return action_model

class ActionModel(models.Model):

    actions = ActionManager()

    type = models.IntegerField()

    x_from = models.IntegerField(default=-1)

    y_from = models.IntegerField(default=-1)

    x_to = models.IntegerField(default=-1)

    y_to = models.IntegerField(default=-1)

    option = models.IntegerField(default=-1)

    def get_changes(self):
        return [(c.x, c.y) for c in ChangeModel.objects.filter(action=self)]

    def get_action(self, state):

        changes = self.get_changes()
        pieces = state.get_pieces()
        previous = state.previous.get_pieces()

        if self.type == 0:
            piece = pieces[self.x_to][self.y_to]
            return PlaceAction(piece, changes)

        elif self.type == 1:
            piece = previous[self.x_from][self.y_from]
            return MoveAction(piece, self.x_to, self.y_to, changes)

        elif self.type == 2:
            piece = previous[self.x_from][self.y_from]
            return RemoveAction(piece, changes)

class ChangeModel(models.Model):

    action = models.ForeignKey(ActionModel, on_delete=models.CASCADE)

    x = models.IntegerField()

    y = models.IntegerField()