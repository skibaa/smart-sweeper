from django.http import HttpResponseRedirect
import logging

#AppEngine imports
#from google.appengine.ext.db import djangoforms
from google.appengine.api import users


#Django imports
from django.core.urlresolvers import reverse
from django.newforms import forms
from django.newforms import fields
from django.shortcuts import render_to_response

#Local imports
from game.models import *

class NewGameForm(forms.Form):
    board_name = fields.ChoiceField(required=True)

    def set_board_choices(self):
        bound_field = self['board_name']
        choices = [('', '[Select board]')]
        def add_names(aModel):
            for b in aModel.all():
                pair = (b.name, b.name)
                choices.append(pair)
        add_names(BoardType)
        add_names(RectangleBoardType)
        bound_field.field.choices = choices
    
def login_required(func):
  """Decorator that redirects to the login page if you're not logged in."""
  def login_wrapper(request, *args, **kwds):
    if users.get_current_user() is None:
      return HttpResponseRedirect(
          users.create_login_url(request.get_full_path().encode('utf-8')))

    return func(request, *args, **kwds)
  return login_wrapper

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
    logging.debug("form bound %s", form)
    if form.is_valid(): # All validation rules pass
        # Process the data in form.cleaned_data
        g = Game(
            user=user,
            isComplete=False,
            boardTypeName=form.clean_data['board_name']
        )
        g.put() #Save new game to db, and redirect there
        return HttpResponseRedirect(
            reverse('game.views.game', args=(g.key().id(),))) # Redirect after POST

    return render_to_response ("home/new_game_form.html", {
        'user': user,
        'form': form,
    })

@login_required
@game_required
def game(request):
    user = users.get_current_user()
    game = request.game
    return render_to_response ("boards/%s.html"%game.boardTypeName, {
        'user': user,
        'game': game,
        'logout_url': users.create_logout_url('/'),
    })
