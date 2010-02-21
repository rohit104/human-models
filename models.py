from google.appengine.ext import db

class Document(db.Model):
    title = db.StringProperty()
    body = db.TextProperty()
    document_id = db.IntegerProperty()
    date = db.DateTimeProperty(auto_now=True)

class Tag(db.Model):
    word = db.IntegerProperty()
    topic = db.IntegerProperty()
    document_id = db.IntegerProperty()
    user_id = db.IntegerProperty()
    word_string = db.StringProperty()
    date = db.DateTimeProperty(auto_now_add=True)
