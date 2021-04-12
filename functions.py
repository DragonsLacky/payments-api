def payment_method_to_json(payment_method):
    if payment_method:
        if payment_method.type == 'credit_cards':
            payment_method_json = {'id': payment_method.id,
                                   'type': payment_method.type,
                                   'cc_number': payment_method.cc_number,
                                   'cvc': payment_method.cvc,
                                   'valid_month': payment_method.valid_month,
                                   'valid_year': payment_method.valid_year,
                                   'card_type': payment_method.card_type.__str__()}
            return payment_method_json
        elif payment_method.type == 'paypal':
            payment_method_json = {'id': payment_method.id,
                                   'type': payment_method.type,
                                   'email': payment_method.email,
                                   'password': payment_method.password,
                                   }
            return payment_method_json


def payment_methods_to_json_array(payment_methods):
    payment_method_json = []
    for pm in [p for p in payment_methods if p.type == 'credit_cards']:
        payment_method_json.append({'id': pm.id,
                                    'type': pm.type,
                                    'cc_number': pm.cc_number,
                                    'cvc': pm.cvc,
                                    'valid_month': pm.valid_month,
                                    'valid_year': pm.valid_year,
                                    'card_type': pm.card_type.__str__()
                                    })
    for pm in [p for p in payment_methods if p.type == 'paypal']:
        payment_method_json.append({'id': pm.id,
                                    'type': pm.type,
                                    'email': pm.email,
                                    'password': pm.password
                                    })
    return payment_method_json


def transaction_to_json(transaction):
    return {'id': transaction.id,
            'amount': transaction.amount,
            'date': transaction.date,
            'completed': transaction.completed,
            'user': {
                'id': transaction.user.id,
                'funds': transaction.user.funds
            }
            }


def transactions_to_json_array(transactions):
    transactions_json = []
    for transaction in transactions:
        transactions_json.append({
            'id': transaction.id,
            'amount': transaction.amount,
            'date': transaction.date,
            'completed': transaction.completed,
            'user': {
                'id': transaction.user.id,
                'funds': transaction.user.funds
            }
        })
    return transactions_json
