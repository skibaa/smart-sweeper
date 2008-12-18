from google.appengine.ext import db
import logging

class UserPrefs(db.Model):
    user = db.UserProperty()

def find_subclasses(module, clazz):
    for name in dir(module):
        o = getattr(module, name)
        try:
            if (o != clazz) and issubclass(o, clazz):
                yield name, o
        except TypeError: pass

class BoardType(db.Model):
    name = db.StringProperty()

    def getBoardsByName(name):
        for clazz in find_subclasses(game.models, BoardType):
            for res in clazz.gql("WHERE name=:name", name=name):
                yield res

class RectangleBoardType(BoardType):
    width = db.IntegerProperty()
    height = db.IntegerProperty()

class Game(db.Model):
    user = db.UserProperty()
    isComplete = db.BooleanProperty()
    startDate = db.DateTimeProperty(auto_now_add = 1)
    boardTypeName = db.StringProperty()
    
    def getBoardType(self):
        if self.key == None:
            self.put() # so key is known
        boardTypes = list(BoardType.getBoardByName(boardTypeName))
        assert len(boardTypes) == 1       
        return boardTypes[0]
    
    def startGame(self):
        board_id=str(self.getBoardType().key)
        init_cells = Cell.gql("WHERE boardOrGameId=:boardId", board_id)
        for cell in init_cells:
            cell.clone(board_id).put()

class Cell(db.Model):
    boardOrGameKey = db.StringProperty() #board id before game, game id later
    coord = db.StringProperty() #coordinates of me - depends on board type
    isOpen = db.BooleanProperty()
    isBomb = db.BooleanProperty()
    neighboursCoords = db.StringListProperty()

    def init(self, boardOrGameKey, neighbours):
        self.boardOrGameKey=boardOrGameKey
        self.isOpen=False
        self.isBomb=False
        for neighbour in neighbours:
            his_neighbours = set(neighbour.neighboursCoords)
            if not his_neighbours.contains(self.coord):
                neighbour.neighbours.add(self.coord)
            self.neighboursCoords.add(neighbour.coord)

    def clone(self, boardOrGameKey):
        return Cell(
            coord=self.coord,
            boardOrGameId=boardOrGameKey,
            isOpen=self.isOpen,
            isBomb=self.isBomb,
            neighboursCoords=self.neighboursCoords
        )
