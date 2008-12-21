from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'game.views.index'),
    (r'^admin/$', 'game.views.admin'),
    (r'^admin/board/new/$', 'game.views.new_board'),
    (r'^game/new/$', 'game.views.new_game'),
    (r'game/(\d+)/$', 'game.views.game'),
)
