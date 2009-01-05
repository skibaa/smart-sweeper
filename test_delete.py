from google.appengine.ext import db
from time import time

print 'Content-Type: text/plain'
print ''

total_t=time()

class C(db.Model):
 i=db.IntegerProperty()
 
for i in range(10):
    t=time()
    count=0
    for c in C.all():
        c.delete()
        count+=1
    if not count: break
    print "deleted", count, time()-t

print "total time:", time()-total_t