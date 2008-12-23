from google.appengine.ext import db
from random import randint

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
        for cell in game.cell_set:
            (row, col)=cell.coord.split()
            if cell.is_open:
                if cell.is_bomb:
                    val='B'
                else:
                    from game import engine
                    val=engine.neighbours_bombs(cell)
            else:
                val='&nbsp;'
            cells[int(row)][int(col)] = {'cell':cell, 'val':val}
            
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
                cell = Cell(
                    coord=self._str_coord(r, c),
                    neighbours_coords=self._calc_neighbours_coords(r, c),
                    board=self
                    )
                cell.put()

class Game(db.Model):
    user = db.UserProperty()
    is_complete = db.BooleanProperty()
    is_won = db.BooleanProperty()
    start_date = db.DateTimeProperty(auto_now_add = 1)
    board = db.ReferenceProperty(BoardType)

class Cell(db.Model):
    coord = db.StringProperty() #coordinates of me - depends on board type
    is_open = db.BooleanProperty()
    is_bomb = db.BooleanProperty()
    neighbours_coords = db.StringListProperty()
    board = db.ReferenceProperty(BoardType)
    game = db.ReferenceProperty(Game) #prototype Cell if game==None