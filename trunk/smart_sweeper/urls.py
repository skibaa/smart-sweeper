from django.conf.urls.defaults import *
import settings

urlpatterns = patterns('',
    (r'^$', 'game.views.index'),
    (r'^game/new/$', 'game.views.new_game'),
    (r'game/(\d+)/$', 'game.views.game'),
)
