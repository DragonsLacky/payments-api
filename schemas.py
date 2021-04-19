from marshmallow_sqlalchemy import SQLAlchemySchema, SQLAlchemyAutoSchema, auto_field
from marshmallow_sqlalchemy.fields import Nested
from marshmallow import fields
from models import UserPayments, Transaction, PayPal, CreditCards


class UserPaymentsSchema(SQLAlchemySchema):
    class Meta:
        model = UserPayments
        load_instance = True
        # include_relationships = True
        fields = ('id', 'funds')


class TransactionSchema(SQLAlchemySchema):
    class Meta:
        model: Transaction
        load_instance = True
        # include_fk = False
        fields = ('id', 'amount', 'date', 'completed', 'user')

    user = Nested(UserPaymentsSchema)


class PayPalSchema(SQLAlchemySchema):
    class Meta:
        model = PayPal
        load_instance = True
        fields = ('id', 'type', 'email', 'password')


class CreditCardSchema(SQLAlchemySchema):
    class Meta:
        model = CreditCards
        load_instance = True
        fields = ('id', 'type', 'cc_number', 'cvc', 'valid_month', 'valid_year', 'card_type')

    def get_card_type(self, obj):
        return obj.card_type.__str__()

    card_type = fields.Method('get_card_type')
