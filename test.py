from google.appengine.ext import db
from time import time

print 'Content-Type: text/plain'
print ''

total_t=time()
class Root(db.Model):
    pass

class C(db.Model):
 i=db.TextProperty()

t1000="a"*10000

def add_in_transaction(root, text, amount):
     for j in range(amount):
        c=C(parent=root, i=text)
        c.put()

print "with transactions - big"
for i in range(5):
    t=time()
    root=Root()
    root.put()
    db.run_in_transaction(add_in_transaction, root, t1000, 10)
    print time()-t
print "without transactions - big"
for i in range(5):
    t=time()
    root=Root()
    root.put()
    add_in_transaction(None, t1000, 10)
    print time()-t
print "without transactions - small"
for i in range(5):
    t=time()
    root=Root()
    root.put()
    add_in_transaction(None, "a", 10)
    print time()-t

print "total time:", time()-total_t