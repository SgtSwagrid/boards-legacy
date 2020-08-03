from games.games.common.action import *
from games.games.common.input import *
from games.games.common.state import *

class Handler:

    event = BoardEvent

    def apply(self, state, display, event):
        return None, display

    def display(self, state, display):
        return display

class PlaceHandler(Handler):

    def __init__(self, type):
        self.type = type

    def apply(self, state, display, event):

        clicked = Piece(self.type, state.turn.current, event.x, event.y)

        if state.game.place_valid(state, clicked):
            state = state.push_action(PlaceAction(clicked))
            state = state.game.place_piece(state, clicked)
            return state, display

        return None, display

    def display(self, state, display):

        for x in range(0, state.game.width):
            for y in range(0, state.game.height):

                piece = Piece(self.type, state.turn.current, x, y)
                if state.game.place_valid(state, piece):
                    texture = self.type.texture(state.turn.current)
                    display = display.add_texture(x, y, Texture(texture, 0.2))\
                        .add_texture(x, y, state.game.place_icon)

        return display

class MoveHandler(Handler):

    def apply(self, state, display, event):

        clicked = state.pieces[event.x][event.y]

        if len(display.selections) > 0:
            pos = display.selections[0]
            selected = state.pieces[pos[0]][pos[1]]

            if state.game.move_valid(state, selected, event.x, event.y):
                moved = selected.at(event.x, event.y)
                action = MoveAction(moved, event.x, event.y)
                state = state.push_action(action)
                state = state.game.move_piece(
                    state, selected, event.x, event.y)
                return state, display.clear_selections()

        if state.game.moveable(state, clicked):
            return None, display.clear_selections().select(event.x, event.y)

        return None, display.clear_selections()

    def display(self, state, display):

        if len(display.selections) > 0:
            pos = display.selections[0]
            selected = state.pieces[pos[0]][pos[1]]

            for x in range(0, state.game.width):
                for y in range(0, state.game.height):

                    if state.game.move_valid(state, selected, x, y):
                        texture = state.game.attack_icon if state.enemy(x, y) else\
                            Texture(selected.type.texture(state.turn.current), 0.2)
                        display = display.add_texture(x, y, texture)

        return display

class RemoveHandler(Handler):

    def apply(self, state, display, event):

        clicked = state.pieces[event.x][event.y]

        if state.game.remove_valid(state, clicked):
            state = state.push_action(RemoveAction(clicked))
            state = state.game.remove_piece(state, clicked)
            return state, display

        return None, display

    def display(self, state, display):

        for x in range(0, state.game.width):
            for y in range(0, state.game.height):

                if state.game.remove_valid(state, state.pieces[x][y]):
                    display = display.add_texture(x, y, state.game.attack_icon)\
                        .enable_buffering(x, y)

        return display