from google.appengine.ext import db

class UserPrefs(db.Model):
    user = db.UserProperty()

class BoardType(db.Model):
    name = db.StringProperty()

class RectangleBoardType(BoardType):
    width = db.IntegerProperty()
    height = db.IntegerProperty()

class Game(db.Model):
    user = db.UserProperty()
    isComplete = db.BooleanProperty()
    startDate = db.DateTimeProperty(auto_now_add = 1)
    boardTypeName = db.StringProperty()