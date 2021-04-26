from app import db
from werkzeug.security import generate_password_hash, check_password_hash
import enum
# from marshmallow_sqlalchemy import SQLAlchemySchema, SQLAlchemyAutoSchema, auto_field
# from marshmallow_sqlalchemy.fields import Nested
# from marshmallow import fields




class MethodType(enum.Enum):
    paypal = 1
    card = 2


class CardType(enum.Enum):
    master = 1
    visa = 2


class UserPayments(db.Model):
    __tablename__ = "user_payments"
    id = db.Column(db.Integer, primary_key=True)
    funds = db.Column(db.Float)
    payment_methods = db.relationship('PaymentMethods')


class Transaction(db.Model):
    __tablename__ = "transactions"
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime)
    completed = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey('user_payments.id'))
    user = db.relationship('UserPayments', backref="user_payments")


class PaymentMethods(db.Model):
    __tablename__ = 'payment_methods'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user_payments.id'), nullable=False)

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'payment_methods'
    }


class CreditCards(PaymentMethods):
    __tablename__ = "credit_cards"
    cc_number = db.Column(db.String(16))
    cvc = db.Column(db.String(3))
    valid_month = db.Column(db.String(2))
    valid_year = db.Column(db.String(2))
    card_type = db.Column(db.Enum(CardType))

    __mapper_args__ = {
        'polymorphic_identity': 'credit_cards',
    }


class PayPal(PaymentMethods):
    __tablename__ = "paypal"
    email = db.Column(db.String)
    password = db.Column(db.String(128))

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    __mapper_args__ = {
        'polymorphic_identity': 'paypal',
    }


# ####
# # Marshmallow schemas
#
# class UserPaymentsSchema(SQLAlchemySchema):
#     class Meta:
#         model = UserPayments
#         load_instance = True
#         # include_relationships = True
#         fields = ('id', 'funds')
#
#
# class TransactionSchema(SQLAlchemySchema):
#     class Meta:
#         model: Transaction
#         load_instance = True
#         # include_fk = False
#         fields = ('id', 'amount', 'date', 'completed', 'user')
#
#     user = Nested(UserPaymentsSchema)
#
#
# class PayPalSchema(SQLAlchemySchema):
#     class Meta:
#         model = PayPal
#         load_instance = True
#         fields = ('id', 'type', 'email', 'password')
#
#
# class CreditCardSchema(SQLAlchemySchema):
#     class Meta:
#         model = CreditCards
#         load_instance = True
#         fields = ('id', 'type', 'cc_number', 'cvc', 'valid_month', 'valid_year', 'card_type')
#
#     def get_card_type(self, obj):
#         return obj.card_type.__str__()
#
#     card_type = fields.Method('get_card_type')
