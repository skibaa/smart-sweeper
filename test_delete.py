from google.appengine.ext import db
from time import time

print 'Content-Type: text/plain'
print ''

total_t=time()

class C(db.Model):
 pass
 
db.delete(C.all())

print "total time:", time()-total_t