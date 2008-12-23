from random import randint
from game.models import *

def start_game(game):
    for cell in game.board.cell_set:
        if cell.game:
            continue # ignore cells belonging to other games
        newcell = Cell(
            coord=cell.coord,
            neighbours_coords=cell.neighbours_coords,
            board=cell.board,
            game=game
        )
        newcell.put()
    game.put() #so the cell_set is updated
    cells = [c for c in game.cell_set] #to overcome Datastore limit of 1000
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
    cell.neighbours_bombs_cached=neighbours_bombs(cell)
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
