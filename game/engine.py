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

def cell_neighbours(cell):
    return cell.gql("""WHERE coord in :coords
        and board=:board
        and game=:game
        order by coord
        """,
        coords=cell.neighbours_coords,
        board=cell.board,
        game=cell.game)

def neighbours_bombs(cell):
    i=0
    for neighbour in cell_neighbours(cell):
        if neighbour.is_bomb:
            i += 1
    return i

def open(cell):
    if cell.is_open:
        return
    cell.is_open=True
    cell.put()
    if cell.is_bomb:
        cell.game.is_complete=True
        cell.game.put()
        return
    if not neighbours_bombs(cell): #if all neighbours are clean, open them
        for n in cell_neighbours(cell):
            open(n)
