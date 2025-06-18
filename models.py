from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()
#with app.app_context():
    #db.create_all()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(512), unique=True)
    password = db.Column(db.String(512))

class Trade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False)
    entry_date = db.Column(db.DateTime, nullable=False)
    exit_date = db.Column(db.DateTime)
    entry_price = db.Column(db.Float, nullable=False)
    exit_price = db.Column(db.Float)
    quantity = db.Column(db.Float, nullable=False)
    position = db.Column(db.String(10), nullable=False)  # long/short
    strategy = db.Column(db.String(50))
    notes = db.Column(db.Text)
    pnl = db.Column(db.Float)
    fees = db.Column(db.Float)
    image_path = db.Column(db.String(100))  # New field for image path
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return f'<Trade {self.symbol} {self.position} {self.entry_date}>'
    
