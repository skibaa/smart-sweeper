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

class Game(db.Model):
    user = db.UserProperty()
    is_complete = db.BooleanProperty()
    start_date = db.DateTimeProperty(auto_now_add = 1)
    board_type = db.ReferenceProperty(BoardType)

    def start_game(self):
        for cell in Cell.get_by_board(self.board_type):
            cell_in_game=cell.create_attached_to_game(self)
            cell_in_game.put()


class Cell(db.Model):
    coord = db.StringProperty() #coordinates of me - depends on board type
    isOpen = db.BooleanProperty()
    isBomb = db.BooleanProperty()
    neighbours_coords = db.StringListProperty()
    boardType = db.ReferenceProperty(BoardType)
    game = db.ReferenceProperty(Game) #prototype Cell if game==None

    def set_neighbours(self, neighbours):
        for neighbour in neighbours:
            if not self.coord in neighbour.neighbours_coords:
                neighbour.neighbours_coords += [self.coord]
            self.neighbours_coords += [neighbour.coord]

    def create_attached_to_game(self, game):
        new_cell = Cell(coord=self.coord,
            neighbours_coords=self.neighboursCoords,
            board_type=self.board_type,
            game=game
        )

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

