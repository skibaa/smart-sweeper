from game.models import RectangleBoardType
from django.http import HttpResponseRedirect
import logging

#AppEngine imports
#from google.appengine.ext.db import djangoforms
from google.appengine.ext.webapp import template
from google.appengine.api import users


#Django imports
from django.core.urlresolvers import reverse
from django.newforms import forms
from django.newforms import fields
from django.shortcuts import render_to_response

#Local imports
from game.models import *

class NewGameForm(forms.Form):
    board = fields.ChoiceField(required=True)

    def set_board_choices(self):
        bound_field = self['board']
        choices = [('', '[Select board]')]
        def add_names(aModel):
            for b in aModel.all():
                pair = (b.key(), b.name)
                choices.append(pair)
        add_names(BoardType)
        add_names(RectangleBoardType)
        bound_field.field.choices = choices
    
class NewBoardForm(forms.Form):
    name = fields.CharField(required=True)
    bombs = fields.IntegerField(required=True)
    board = fields.ChoiceField(required=True)
    width = fields.IntegerField(required=True)
    height = fields.IntegerField(required=True)

    def set_board_choices(self):
        bound_field = self['board']
        choices = [('', '[Select board type]'),('RectangleBoardType', 'Rectangle board')]
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

def game_required(func):
  """Decorator that processes the game_id handler argument."""
  def issue_wrapper(request, game_id, *args, **kwds):
    game = Game.get_by_id(int(game_id))
    if game is None:
      return HttpResponseNotFound('No game exists with that id (%s)' %
                                  game_id)
    request.game = game
    return func(request, *args, **kwds)
  return issue_wrapper

def index(request):
    user = users.get_current_user()
    games = Game.gql("WHERE user=:user AND isComplete=FALSE", user=user).fetch(100)

    return render_to_response ('home/index.html', {
        'user': user,
        'games': games,
        'new_game_link': '/game/new',
        'logout_url': users.create_logout_url('/'),
        'login_url': users.create_login_url('/')
    })

@login_required
def new_game(request):
    user = users.get_current_user()
    if request.method != 'POST': # If the form has been submitted...
        form = NewGameForm() # An unbound form
        form.set_board_choices()
        return render_to_response ("home/new_game_form.html", {
            'user': user,
            'form': form,
        })

    form = NewGameForm(request.POST) # A form bound to the POST data
    form.set_board_choices()
    if not form.is_valid(): # All validation rules pass
        return render_to_response ("home/new_game_form.html", {
            'user': user,
            'form': form,
        })    # Process the data in form.cleaned_data

    board = BoardType.get(form.clean_data['board'])
    g = Game(
        user=user,
        isComplete=False,
        board = board
    )
    g.put() #Save new game to db, and redirect there
    g.start_game()
    g.put()
    return HttpResponseRedirect(
        reverse('game.views.game', args=(g.key().id(),))) # Redirect after POST

@login_required
@game_required
def game(request):
    user = users.get_current_user()
    game = request.game
    cells = game.board.get_cells_for_template(game)
    return render_to_response (game.board.get_template(), {
        'user': user,
        'game': game,
        'cells': cells,
        'logout_url': users.create_logout_url('/'),
    })

@admin_required
def admin(request):
    boards = RectangleBoardType.all().fetch(1000) #TODO: find out how to use polymorphism
    return render_to_response ("admin/index.html", {'boards':boards})

@admin_required
def view_board(request, board_key):
    board = BoardType.get(board_key)
    return render_to_response ("admin/edit_board.html", {'board':board})

@admin_required
def del_board(request, board_key):
    board = BoardType.get(board_key)
    for cell in board.cell_set:
        cell.delete()
    board.delete()
    return render_to_response ("admin/edit_board.html", {'board':board})

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


    board_class = globals()[form.clean_data['board']]
    #TODO: use reflection to allow any class
    assert board_class==RectangleBoardType
    board = board_class(name=form.clean_data['name'],
        bombs=form.clean_data['bombs'],
        width=form.clean_data['width'],
        height=form.clean_data['height'])
    board.put()
    board.init_cells()
    board.put()
    assert board.cell_set.fetch(1)[0]
    return render_to_response("admin/index.html",
        {'boards':RectangleBoardType.all().fetch(1000)})

