from app import db


class Transaction(db.Model):
    __tablename__ = "transactions"
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime)
    completed = db.Column(db.Boolean)
    user_id = db.Column(db.String, nullable=False)
    user = db.relationship('UserPayments', db.backref('transactions'))
