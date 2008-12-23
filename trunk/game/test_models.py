#from game.models import RectangleBoardType
import unittest

#from game.models import *

#class TestSimpleModel(unittest.TestCase):
#    def test_creation(self):
#        g = RectangleBoardType(name='test',bombs=3, width=3, height=3)
#        g.put()
#        g1 = RectangleBoardType.gql('WHERE name=:name', 'test')
#        g1.delete()
#        assertEquals(g1.bombs, 3)

def test_calculations():
   assert 2+2 == 4