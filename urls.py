from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^game/$', 'game.views.index'),
    (r'^admin/$', 'game.views.admin'),
    (r'^admin/board/new/$', 'game.views.new_board'),
    (r'^admin/board/(?P<board_key>\w+)/$', 'game.views.view_board'),
    (r'^admin/board/(?P<board_key>\w+)/delete/$', 'game.views.del_board'),
    (r'^game/new/$', 'game.views.new_game'),
    (r'game/open/(?P<cell_id>\d+)/$', 'game.views.game_open'),
    (r'game/flag/(?P<cell_id>\d+)/$', 'game.views.game_flag'),
)
