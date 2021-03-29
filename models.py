from app import db
from werkzeug.security import generate_password_hash, check_password_hash
import enum


class MethodType(enum.Enum):
    paypal = 1
    card = 2


class CardType(enum.Enum):
    master = 1
    visa = 2


class UserPayments(db.Model):
    __tablename__ = "user_payments"
    id = db.Column(db.String, primary_key=True)
    funds = db.Column(db.Float)
    payment_methods = db.relationship('PaymentMethods')


class PaymentMethods(db.Model):
    __tablename__ = 'payment_methods'
    id = db.Column(db.String, primary_key=True)
    type = db.Column(db.Enum(MethodType), nullable=False)
    user_id = db.Column(db.String, db.ForeignKey('user_payments.id'), nullable=False)

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'payment_methods'
    }


class CreditCards(PaymentMethods):
    __tablename__ = "credit_cards"
    cc_number = db.Column(db.String(16), nullable=False)
    cvc = db.Column(db.String(3), nullable=False)
    valid_month = db.Column(db.String(2), nullable=False)
    valid_year = db.Column(db.String(2), nullable=False)
    card_type = db.Column(db.Enum(CardType), nullable=False)


class PayPal(PaymentMethods):
    __tablename__ = "paypal"
    email = db.Column(db.String, nullable=False)
    password = db.Column(db.String(128))

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Transaction(db.Model):
    __tablename__ = "transactions"
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime)
    completed = db.Column(db.Boolean)
    user_id = db.Column(db.String, nullable=False)
    user = db.relationship('UserPayments', db.backref('transactions'))
