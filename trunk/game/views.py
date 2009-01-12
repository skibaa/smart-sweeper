from google.appengine.ext.webapp import template #according to http://code.google.com/appengine/articles/djangoforms.html

from django.http import HttpResponseRedirect

#AppEngine imports
from google.appengine.api import users
#from google.appengine.ext.db import djangoforms

#Django imports
from django.core.urlresolvers import reverse
from django.newforms import forms
from django.newforms import fields
from django.shortcuts import render_to_response

#Local imports
from game.models import *
from game import engine
from game.engine import RectangleBoard

class NewGameForm(forms.Form):
    board = fields.ChoiceField(required=True)

    def set_board_choices(self):
        bound_field = self['board']
        choices = [('', '[Select board]')]
        for b in BoardModel.all():
            pair = (b.key(), engine.unsanitize_key(b.key().name()))
            choices.append(pair)
        bound_field.field.choices = choices
    
class NewBoardForm(forms.Form):
    name = fields.CharField(required=True)
    bombs = fields.IntegerField(required=True)
    board = fields.ChoiceField(required=True)
    width = fields.IntegerField(required=True)
    height = fields.IntegerField(required=True)

    def set_board_choices(self):
        bound_field = self['board']
        choices = [('', '[Select board type]'),(RectangleBoard.__name__, 'Rectangle board')]
        bound_field.field.choices = choices

def login_required(func):
  """Decorator that redirects to the login page if you're not logged in."""
  def login_wrapper(request, *args, **kwds):
    if users.get_current_user() is None:
      return HttpResponseRedirect(
          users.create_login_url(request.get_full_path().encode('utf-8')))

    return func(request, *args, **kwds)
  return login_wrapper

def admin_required(func):
  """Decorator that redirects to the login page if you're not logged in."""
  def admin_wrapper(request, *args, **kwds):
    if not users.is_current_user_admin():
        return render_to_response("admin/noaccess.html")

    return func(request, *args, **kwds)
  return admin_wrapper

def _get_current_game():
    user = users.get_current_user()
    if not user: return None
    game_key = db.Key.from_path('GameModel', engine.sanitize_key(user.email()))
    return db.get(game_key)

@login_required
def index(request):
    game_model=_get_current_game()
    if game_model:
        return _response_game(game_model.contents)
    else:
        return _show_new_game_form()

def _show_new_game_form():
    form = NewGameForm() # An unbound form
    form.set_board_choices()
    return render_to_response ("home/new_game_form.html", {
        'form': form,
    })

@login_required
def new_game(request):
    if request.method != 'POST': # If the form has been submitted...
        return _show_new_game_form()

    user = users.get_current_user()
    form = NewGameForm(request.POST) # A form bound to the POST data
    form.set_board_choices()
    if not form.is_valid(): # All validation rules pass
        return render_to_response ("home/new_game_form.html", {
            'user': user,
            'form': form,
        })    # Process the data in form.cleaned_data

    board_model = BoardModel.get(form.clean_data['board'])
    game=engine.start_game(board_model.contents)
    game_model = GameModel(
        key_name=engine.sanitize_key(user.email()),
        contents=game
    )
    game_model.put() #Save new game to db, and redirect there
    return HttpResponseRedirect(reverse('game.views.index')) # Redirect after POST

@login_required
def game_open(request, cell_id):
    game_model=_get_current_game()
    game=game_model.contents
    engine.open(game, int(cell_id))
    engine.check_won(game)
    game_model.contents=game
    game_model.save()
    return _response_game(game)

@login_required
def game_flag(request, cell_id):
    game_model=_get_current_game()
    game=game_model.contents
    cell=game.cells[int(cell_id)]
    engine.flag(cell)
    game_model.contents=game
    game_model.save()
    return _response_game(game)

def _response_game(game):
    cells = game.board.cells_for_template(game.cells)
    return render_to_response (game.board.get_template(), {
        'cells': cells,
        'game': game,
        'logout_url': users.create_logout_url('/'),
    })

@admin_required
def admin(request):
    boards = [
        {'key':b.key(),'name':engine.unsanitize_key(b.key().name()),'contents':b.contents}
            for b in BoardModel.all()]
    return render_to_response ("admin/index.html", {'boards':boards})

@admin_required
def view_board(request, board_key):
    board = BoardModel.get(board_key)
    return render_to_response ("admin/edit_board.html", {'board':board})

@admin_required
def del_board(request, board_key):
    db.delete(board_key)
    return HttpResponseRedirect(reverse('game.views.admin'))

@admin_required
def new_board(request):
    if request.method != 'POST': # If the form has been submitted...
        form = NewBoardForm() # An unbound form
        form.set_board_choices()
        return render_to_response ("admin/new_board.html", {
            'form': form,
        })

    form = NewBoardForm(request.POST) # A form bound to the POST data
    form.set_board_choices()
    if not form.is_valid(): # All validation rules pass
        return render_to_response ("admin/new_board.html", {
            'form': form,
        })    # Process the data in form.cleaned_data

    board_kind=form.clean_data['board']
    board_class = globals()[board_kind]
    #TODO: use reflection to allow any class
    assert board_class==RectangleBoard
    board = board_class(
        bombs=form.clean_data['bombs'],
        width=form.clean_data['width'],
        height=form.clean_data['height'])
    board_model=BoardModel(key_name=engine.sanitize_key(form.clean_data['name']))
    board_model.contents=board
    board_model.put()
    return HttpResponseRedirect(reverse('game.views.admin'))

