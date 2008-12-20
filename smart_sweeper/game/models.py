from google.appengine.ext import db
import logging

class UserPrefs(db.Model):
    user = db.UserProperty()

class BoardType(db.Model):
    name = db.StringProperty()

    @classmethod
    def get_view(self):
        return None

    def kind_key(self):
        return self.kind()+' '+str(self.key())

    @classmethod
    def get_by_kind_key(self, kk):
        (kind, key) = kk.split()
        return globals()[kind].get(key)

class RectangleBoardType(BoardType):
    width = db.IntegerProperty()
    height = db.IntegerProperty()

    @classmethod
    def get_view(self):
        return 'boards/rectangle.html'

class BoardTypeExpando(db.Expando):
    #property board_type_key = any_board_type.key()
    #property board_type_kind = any_board_type.kind()

    def _get_board_type(self):
        if (not 'board_type_key' in self.dynamic_properties()) or (not 'board_type_kind' in self.dynamic_properties()):
            return None
        kind=globals()[self.board_type_kind]
        return kind.get(self.board_type_key)

    def _set_board_type(self, aBoard_type):
        if not aBoard_type:
            del self.board_type
        self.board_type_key = aBoard_type.key()
        self.board_type_kind = aBoard_type.kind()

    def _delete_board_type(self):
        del self.board_type_key
        del self.board_type_kind

    _board_type=property(_get_board_type, _set_board_type, _delete_board_type)
    
class Game(BoardTypeExpando):
    user = db.UserProperty()
    is_complete = db.BooleanProperty()
    start_date = db.DateTimeProperty(auto_now_add = 1)

    def start_game(self):
        for cell in Cell.get_by_board(self.board_type):
            cell_in_game=cell.create_attached_to_game(self)
            cell_in_game.put()

    @property
    def cells(self):
        return Cell.get_by_board_and_name(board_type, self)

class Cell(BoardTypeExpando):
    coord = db.StringProperty() #coordinates of me - depends on board type
    isOpen = db.BooleanProperty()
    isBomb = db.BooleanProperty()
    neighbours_coords = db.StringListProperty()

    def init(self, board_type, game, neighbours):
        self.board_type=board_type
        if game and game.has_key():
            self.game = game.key()
        else:
            self.game = None
        for neighbour in neighbours:
            if not self.coord in neighbour.neighbours_coords:
                neighbour.neighbours_coords += [self.coord]
            self.neighbours_coords += [neighbour.coord]

    def create_attached_to_game(self, game):
        new_cell = Cell(coord=self.coord,
            neighbours_coords=self.neighboursCoords
        )
        #TODO see if expando properties can be set in constructor
        new_cell.board_type=self.board_type
        new_cell.game=game

    @property
    def neighbours(self):
        return self.gql("""WHERE :coords in neighbours_coords
            and board_type_key=:btkey
            and board_type_kind=:btkind
            and game=:game""",
            coords=coord,
            btkey=self.board_type_key,
            btkind=self.board_type_kind,
            game=game)

    @classmethod
    def get_by_board(cls, board_type):
        return cls.gql("""WHERE
            board_type_key=:btkey
            and board_type_kind=:btkind
            and game=:game""",
            btkey=board_type.key(),
            btkind=board_type.kind(),
            game=None)

    @classmethod
    def get_by_board_and_game(cls, board_type, game):
        return cls.gql("""WHERE
            board_type_key=:btkey
            and board_type_kind=:btkind 
            and game=:game""",
            btkey=board_type.key(),
            btkind=board_type.kind(),
            game=game)

