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

    def get_cells_for_template(self, game):
        assert game.board == self
        cells = [[i]*self.width for i in range(self.height)]
        wasThere=False
        for cell in game.cell_set.fetch(1000):
            wasThere = True
            (row, col)=cell.coord.split()
            cells[int(row)][int(col)]=cell
        assert wasThere
        return cells

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
                    board=self
                    )
                cell.put()

class Game(db.Model):
    user = db.UserProperty()
    is_complete = db.BooleanProperty()
    start_date = db.DateTimeProperty(auto_now_add = 1)
    board = db.ReferenceProperty(BoardType)

    def start_game(self):
        for cell in self.board.cell_set:
            cell.create_attached_to_game(self)
        self.board.put() #so the cell_set is updated

class Cell(db.Model):
    coord = db.StringProperty() #coordinates of me - depends on board type
    isOpen = db.BooleanProperty()
    isBomb = db.BooleanProperty()
    neighbours_coords = db.StringListProperty()
    board = db.ReferenceProperty(BoardType)
    game = db.ReferenceProperty(Game) #prototype Cell if game==None

    def create_attached_to_game(self, game):
        cell = Cell(coord=self.coord,
            neighbours_coords=self.neighbours_coords,
            board=self.board,
            game=game
        )
        cell.put()
        assert not cell.key()==self.key()

    @property
    def neighbours(self):
        return self.gql("""WHERE :coords in neighbours_coords
            and board=:board
            and game=:game
            order by coord
            """,
            coords=coord,
            btkey=self.board,
            game=game)

