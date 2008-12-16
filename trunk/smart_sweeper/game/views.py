from django.shortcuts import render_to_response
from google.appengine.api import users
from game.models import *

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
        'logout_url': users.create_logout_url('/'),
        'login_url': users.create_login_url('/')
    })

@login_required
@game_required
def game(request):
    user = users.get_current_user()
    game = request.game
    return render_to_response ("boards/%s.html"%game.boardType.name, {
        'user': user,
        'game': game,
        'logout_url': users.create_logout_url('/'),
    })
