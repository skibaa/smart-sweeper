from google.appengine.ext import db
import logging

class UserPrefs(db.Model):
    user = db.UserProperty()

class BoardType(db.Model):
    name = db.StringProperty()
    bombs = db.IntegerProperty()

class RectangleBoardType(BoardType):
    width = db.IntegerProperty()
    height = db.IntegerProperty()

    @classmethod
    def get_template(self):
        return 'boards/rectangle.html'
    
    @staticmethod
    def _str_coord(row, col):
        return "%d %d"%(row, col)

    def _calc_neighbours_coords(self, r, c):
        result_tuples=[(r-1, c-1),(r-1, c), (r-1, c+1),
            (r, c-1),     (r, c+1),
            (r+1, c-1), (r+1, c), (r+1, c+1)]
        result_strings=[]
        for (row, col) in result_tuples:
            if row<0 or col<0:
                continue
            if row>=self.height or col>=self.width:
                continue
            result_strings+=[self._str_coord(row, col)]
        return result_strings

    def init_cells(self):
        for r in range(0, self.height):
            for c in range(0, self.width):
                cell = Cell(coord=self._str_coord(r, c),
                    neighbours_coords=self._calc_neighbours_coords(r, c),
                    boardType=self
                    )
                cell.put()

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
            and game=:game
            order by coord
            """,
            coords=coord,
            btkey=self.board_type_key,
            btkind=self.board_type_kind,
            game=game)

