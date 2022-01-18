import flask_sqlalchemy

db = flask_sqlalchemy.SQLAlchemy()

class rooms(db.Model):
    __tablename__ = "rooms"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    admin = db.Column(db.String(50))
    question = db.Column(db.String(5000))
    yes = db.Column(db.Integer)
    no = db.Column(db.Integer)

