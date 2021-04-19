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
