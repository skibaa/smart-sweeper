#from game.models import RectangleBoardType
from game.models import BoardType
import unittest
from game.models import *

#from game.models import *

#class TestSimpleModel(unittest.TestCase):
#    def test_creation(self):
#        g = RectangleBoardType(name='test',bombs=3, width=3, height=3)
#        g.put()
#        g1 = RectangleBoardType.gql('WHERE name=:name', 'test')
#        g1.delete()
#        assertEquals(g1.bombs, 3)

def test_calculations():
   bt=BoardType(name='a', bombs=1)
   bt.put()
   bt1=BoardType.gql('where name=:name', name='a').fetch(1)[0]
   assert bt1.bombs==1