from google.appengine.ext import db
from game.dbext import PickledProperty
import pickle

class UserPrefs(db.Model):
    user = db.UserProperty()

class Board(object):
    bombs=0

    def __str__(self):
        return "Board with %d bombs" % self.bombs

    def get_template(self):
        return None

    def create_cells(self):
        return []

    def cells_for_template(self, cells):
        return cells

class Game(object): #key_name must be user id
    is_complete = False
    is_won = False
    board = None #a Board instance
    cells = None #[Cell, Cell, ...]

class BoardModel(db.Model):
    #key name = board name
    contents = PickledProperty(Board)

class GameModel(db.Model):
    #key name = user
    contents = PickledProperty(Game)

