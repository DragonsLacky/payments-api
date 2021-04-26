from schemas import TransactionSchema, UserPaymentsSchema, PayPalSchema, CreditCardSchema


def payment_method_to_json(payment_method):
    if payment_method:
        if payment_method.type == 'credit_cards':
            payment_method_schema = CreditCardSchema()
        elif payment_method.type == 'paypal':
            payment_method_schema = PayPalSchema()

        payment_method_dump = payment_method_schema.dump(payment_method)
        return payment_method_dump


def payment_methods_to_json_array(payment_methods):
    payment_method_json = []

    for payment_method in payment_methods:
        payment_method_json.append(payment_method_to_json(payment_method))
    return payment_method_json


def transaction_to_json(transaction):
    transaction_schema = TransactionSchema()

    transaction_dump = transaction_schema.dump(transaction)

    return transaction_dump


def transactions_to_json_array(transactions):
    transactions_json = []

    for transaction in transactions:
        transactions_json.append(transaction_to_json(transaction))
    return transactions_json


def check_if_credit_card_exists(payment_method):
    from models import CardType, CreditCards

    curr_card_type = CardType.master
    if payment_method.card_type == "visa":
        curr_card_type = CardType.visa

    credit_cards = CreditCards.query.filter_by(user_id=payment_method.user_id,
                                               cc_number=payment_method.cc_number,
                                               cvc=payment_method.cvc,
                                               valid_month=payment_method.valid_month,
                                               valid_year=payment_method.valid_year,
                                               card_type=curr_card_type).count()
    if credit_cards > 0:
        return True
    return False


def check_if_paypal_exists(user_id, email, password):
    from models import PayPal
    
    paypals = PayPal.query.filter_by(user_id=user_id)

    for paypal in paypals:
        if paypal.email == email and paypal.check_password(password):
            return True
    return False
