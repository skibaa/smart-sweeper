import logging
from random import randint
from game.models import *

logger=logging.getLogger("smartSweeper.engine")

class Cell(object):
    neighbours=[] #indeces of neighbours
    is_open = False
    is_bomb = False
    is_flag = False
    bombs_around_cached = None

class RectangleBoard(Board):
    def  __init__(self, bombs, width, height):
        self.bombs = bombs
        self.width = width
        self.height = height

    def __str__(self):
        return "%d x %d rectangle with %d bombs"%(self.width, self.height, self.bombs)

    def get_template(self):
        return 'boards/rectangle.html'

    def cells_for_template(self, cells):
        res = []
        i=0
        for row in range(self.height):
            res+=[[{'key':i+col,'value':render_cell(cells[i+col])}
                for col in range(self.width)]]
            i+=self.width
        return res

    def _calc_neighbours_indeces(self, index):
        w=self.width
        possibles=index-w-1,  index-w,    index-w+1, \
            index-1,                        index+1, \
            index+w-1,  index+w,    index+w+1
        max_i=self.width*self.height-1
        return [i for i in possibles if i>=0 and i<=max_i]

    def create_cells(self):
        res = [Cell() for i in range(self.width * self.height)]
        for i,v in enumerate(res):
            v.neighbours=[n for n in self._calc_neighbours_indeces(i)]
        return res

def start_game (board):
    logger.debug("start_game1")
    game=Game()
    game.board=board
    game.cells=board.create_cells()
    empty_cells=game.cells[:] #make a shallow copy of the list
    for i in range(game.board.bombs):
        randindex=randint(0, len(empty_cells)-1)
        cell = empty_cells.pop(randindex)
        #the cell is same in cells and empty_cells because of shallow copy
        cell.is_bomb=True
    return game

def bombs_around(game, index):
    cell=game.cells[index]
    if cell.bombs_around_cached is None:
        assert cell.is_open
        cell.bombs_around_cached = len(filter(
            lambda(c):game.cells[c].is_bomb,
            cell.neighbours))
    return cell.bombs_around_cached

def open(game, index):
    cell=game.cells[index]
    if cell.is_open:
        return
    cell.is_open=True
    if cell.is_bomb:
        game.is_complete=True
        return
    if bombs_around(game, index)==0: #if all neighbours are clean, open them
        for n in cell.neighbours:
            open(game, n)

def check_won(game):
    if game.is_won:
        return
    closed_cells=len(filter(lambda(c):not c.is_open, game.cells))
    logger.info("closed cells:%d, bombs hidden:%d", closed_cells, game.board.bombs)
    if game.board.bombs == closed_cells:
        game.is_won=True
        game.is_complete=True

def flag(cell):
    if cell.is_flag:
        cell.is_flag=None
    else:
        cell.is_flag=True

def render_cell(cell):
    if cell.is_open:
        if cell.is_bomb:
            return '/static/images/bomb.png'
        else:
            assert cell.bombs_around_cached is not None
            return '/static/images/'+str(cell.bombs_around_cached)+'.png'
    else:
        if cell.is_flag:
            return '/static/images/flag.png'
        else:
            return '/static/images/closed.png'

def sanitize_key(name):
    return 'key'+name

def unsanitize_key(key_name):
    return key_name[3:]