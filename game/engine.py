import logging
from random import randint
from game.models import *

logging.basicConfig(level=logging.DEBUG)

def bind_cells(game):
    cells=[]
    for cell in game.board.unboundcell_set:
        newcell = BoundCell(
            coord=cell.coord,
            neighbours_coords=cell.neighbours_coords,
            board=cell.board,
            game=game
        )
        cells += [newcell]
    assert cells, "No unbound cells for board"
    return cells

def save_cells(cells):
    for cell in cells:
        cell.save()

def start_game(game):
    cells = bind_cells(game)
    save_cells(cells)
    put_bombs(game, cells)

def put_bombs (game, cells):
    for i in range(game.board.bombs):
        cell = cells[randint(0, len(cells)-1)]
        cell.is_bomb=True
        cell.put()
        cells.remove(cell) #so it does not get a bomb twice

def cell_neighbours(cell, game=None):
    if not game:
        game=cell.game
    for i in cell.neighbours_coords:
        yield game.cell_map[i]

def neighbours_bombs(cell, game=None):
    assert cell.is_open
    if not cell.neighbours_bombs_cached==None:
        return cell.neighbours_bombs_cached
    return len(filter(lambda(c):c.is_bomb, cell_neighbours(cell, game)))

def open(cell, game=None):
    if cell.is_open:
        return
    cell.is_open=True
    cell.neighbours_bombs_cached=neighbours_bombs(cell, game)
    cell.put()
    if not game:
        game=cell.game
    if cell.is_bomb:
        game.is_complete=True
        game.put()
        return
    if cell.neighbours_bombs_cached==0: #if all neighbours are clean, open them
        for n in cell_neighbours(cell, game):
            open(n, game)

def check_won(game):
    logging.info("game won")
    if game.is_won:
        return
    closed_cells=len(filter(lambda(c):not c.is_open, game.boundcell_set))
    logging.info("closed cells:%d, bombs hidden:", closed_cells, game.board.bombs)
    if game.board.bombs == closed_cells:
        game.is_won=True
        game.is_complete=True
        game.put()

def flag(cell):
    if cell.is_flag:
        cell.is_flag=None
    else:
        cell.is_flag=True
    cell.put()

def cells_renderings(game):
    for (coord,cell) in game.cell_map.iteritems():
        if cell.is_open:
            if cell.is_bomb:
                val='B'
            else:
                val=neighbours_bombs(cell, game)
        else:
            if cell.is_flag:
                val='F'
            else:
                val='&nbsp;'
        yield (coord,cell,val)
