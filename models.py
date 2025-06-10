from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
#with app.app_context():
    #db.create_all()

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
    
    def __repr__(self):
        return f'<Trade {self.symbol} {self.position} {self.entry_date}>'