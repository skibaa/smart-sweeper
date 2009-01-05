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
def add_many(text, amount):
    db.put([C(i=text) for i in range(amount)])

print "with transactions"
for i in range(5):
    t=time()
    root=Root()
    root.put()
    db.run_in_transaction(add_in_transaction, root, t1000, 30)
    print time()-t
print "with put many"
for i in range(5):
    t=time()
    root=Root()
    root.put()
    add_many(t1000, 30)
    print time()-t

print "total time:", time()-total_t