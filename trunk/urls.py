from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'game.views.index'),
    (r'^admin/$', 'game.views.admin'),
    (r'^admin/board/new/$', 'game.views.new_board'),
    (r'^admin/board/(?P<board_key>\w+)/$', 'game.views.view_board'),
    (r'^admin/board/(?P<board_key>\w+)/delete/$', 'game.views.del_board'),
    (r'^game/new/$', 'game.views.new_game'),
    (r'game/(\d+)/$', 'game.views.game'),
)
