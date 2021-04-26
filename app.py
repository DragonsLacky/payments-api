from functools import wraps

import connexion
from flask import request, abort
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import time
import jwt
import requests
import json

from consul_functions import get_host_name_IP, get_consul_service, register_to_consul



SECRET = 'SECRETSTUFF'
APIKEY = 'PAYMENT_APIKEY'




def has_role(arg):
    def has_role_inner(fn):
        @wraps(fn)
        def decode_view(*args, **kwargs):
            try:
                headers = request.headers
                if 'Authorization' in headers:
                    token = headers['Authorization'].split(' ')[1]
                    decoded_token = decode_token(token)
                    if 'admin' in decoded_token:
                        return fn(*args, **kwargs)
                    for role in arg:
                        if role in decoded_token['roles']:
                            return fn(*args, **kwargs)
                    abort(404)
                return fn(*args, **kwargs)
            except Exception as e:
                abort(401)

        return decode_view

    return has_role_inner


def decode_token(token):
    return jwt.decode(token, SECRET, algorithms='HS256')


@has_role(['payments'])
def find_all_transactions():
    transactions = Transaction.query.all()
    if transactions:
        return transactions_to_json_array(transactions), 200
    else:
        return {'Message': 'No transactions'}, 404


@has_role(['payments'])
def find_user_transactions(user_id):
    transactions = Transaction.query.filter_by(user_id=user_id).all()
    if transactions:
        return transactions_to_json_array(transactions), 200
    else:
        return {'message': 'No transactions'.format(user_id)}, 404


@has_role(['invoices'])
def transaction_details(transaction_id):
    transaction = Transaction.query.filter_by(id=transaction_id).first()
    if transaction:
        return transaction_to_json(transaction), 200
    else:
        return {'message': 'error not found'}, 404


@has_role(['payments'])
def edit_transaction(transaction_id, transaction_body):
    transaction = Transaction.query.filter_by(id=transaction_id).first()
    if transaction:
        transaction.user_id = transaction_body['user_id']
        transaction.amount = transaction_body['amount']
        transaction.completed = transaction_body['completed']
        transaction.date = datetime.now()
        db.session.add(transaction)
        db.session.commit()
        return transaction_to_json(transaction), 200
    else:
        return {'message': 'error not found'}, 404


@has_role(['payments'])
def save_transaction(transaction_body):

    user_id = transaction_body['user_id']
    user = UserPayments.query.filter_by(id=user_id).first()
    if user is None:
        user = UserPayments(id=user_id, funds=0)
        db.session.add(user)

    transaction = Transaction(date=datetime.now(),
                              amount=transaction_body['amount'],
                              user=user,
                              completed=transaction_body['completed'])
    db.session.add(transaction)
    db.session.commit()


@has_role(['shopping_cart'])
def cart_payment_status(transaction_id):
    transaction = db.session.query(Transaction).filter_by(id=transaction_id).first()
    if transaction:
        return transaction.completed
    else:
        return {'message': 'error not found'}, 404


@has_role(['shopping_cart', 'reserve'])
def rent_payment_status(transaction_id):
    transaction = db.session.query(Transaction).filter_by(id=transaction_id).first()
    if transaction:
        return transaction.completed
    else:
        return {'message': 'error not found'}, 404


@has_role(['payments'])
def find_all_user_payment_methods(user_id):
    payment_methods = PaymentMethods.query.filter_by(user_id=user_id).all()
    if payment_methods:
        return payment_methods_to_json_array(payment_methods), 200
    else:
        return {'message': 'error not found'}, 404


@has_role(['payments'])
def save_user_payment_method(user_id, user_payment_method):
    user = UserPayments.query.filter_by(id=user_id).first()
    if not user:
        user = UserPayments(id=user_id, funds=0)
        db.session.add(user)
        return insert_payment_method(user_payment_method, user_id)
    else:
        return insert_payment_method(user_payment_method, user_id)


def insert_payment_method(user_payment_method, user_id):
    payment_method = {}
    if user_payment_method['type'] == 'credit_cards':
        payment_method = CreditCards(user_id=user_id,
                                     cc_number=user_payment_method['method']['cc_number'],
                                     cvc=user_payment_method['method']['cvc'],
                                     valid_month=user_payment_method['method']['valid_month'],
                                     valid_year=user_payment_method['method']['valid_year'],
                                     card_type=user_payment_method['method']['card_type'])
        if not check_if_credit_card_exists(payment_method):
            db.session.add(payment_method)
        else:
            return {'message': 'Already exists'}, 409
    elif user_payment_method['type'] == 'paypal':
        payment_method = PayPal(email=user_payment_method['method']['email'], user_id=user_id)
        payment_method.set_password(user_payment_method['method']['password'])
        if not check_if_paypal_exists(user_id, user_payment_method['method']['email'],
                                      user_payment_method['method']['password']):
            db.session.add(payment_method)
        else:
            return {'message': 'Already exists'}, 409
    db.session.commit()

    return payment_method_to_json(payment_method), 200


@has_role(['payments'])
def find_user_payment_method_by_id(method_id):
    payment_method = PaymentMethods.query.filter_by(id=method_id).first()
    if payment_method:
        return payment_method_to_json(payment_method), 200
    else:
        return {'message': 'error not found'}, 404


@has_role(['payments'])
def delete_user_payment_method(method_id):
    payment_method = PaymentMethods.query.filter_by(id=method_id).first()
    if payment_method:
        db.session.delete(payment_method)
        db.session.commit()
        return {'message': 'successfully deleted'}, 200
    else:
        return {'message': 'error not found'}, 404


# Only for testing purposes
# Generate token
def auth_microservice(auth_body_microservice):
    apikey = auth_body_microservice['apikey']

    if apikey == 'PAYMENT_APIKEY':
        roles = ['invoices', 'shopping_cart', 'payments']
        sub = 'payments'
    else:
        return {"Message": "API key invalid"}, 401

    user = {"id": 0}

    timestamp = int(time.time())
    payload = {
        "iss": 'my app',
        "iat": int(timestamp),
        "exp": int(timestamp + 600000),
        "sub": sub,
        "roles": roles,
        "user_details": user
    }
    encoded = jwt.encode(payload, SECRET, algorithm="HS256")
    return encoded

def get_discounts_url():

    discounts_address, discounts_port = get_consul_service("discounts")
    
    url = "{}:{}".format(discounts_address, discounts_port)

    if not url.startswith("http"):
        url = "http://{}".format(url)
    
    return url

def discounts_request(user_id, amount, target_function):
    discounts_url = get_discounts_url()
    url = "{}/api/{}/{}".format(discounts_url, target_function, user_id)

    headers = request.headers
    auth_headers = {}
    if 'Authorization' in headers:
        auth_headers["Authorization"] = headers['Authorization']
    
    amount_data = {"PriceToPay": amount}
    
    discounts_response = requests.post(url=url, headers = auth_headers, json=amount_data)

    return discounts_response

@has_role(['shopping_cart'])
def cart_pay(user_id, amount):

    target_function = "applyDiscountForUserBuyingProduct"
    discounts_response = discounts_request(user_id, amount['amount'], target_function)

    return pay(user_id, discounts_response)


@has_role(['shopping_cart', 'reserve'])
def rent_pay(user_id, amount):    

    target_function = "applyDiscountForUserRentingBike"
    discounts_response = discounts_request(user_id, amount['amount'], target_function)
    
    return pay(user_id, discounts_response)


@has_role(['shopping_cart', 'reserve'])
def parking_pay(user_id, amount):

    target_function = "applyDiscountForUserPayingParking"
    discounts_response = discounts_request(user_id, amount['amount'], target_function)

    return pay(user_id, discounts_response)


def pay(user_id, discounts_response):

    discounts_response_json = discounts_response.json()
    
    if discounts_response.status_code != 200:
        discounts_response_json["Source of response"] = "Discounts microservice"
        return discounts_response_json, discounts_response.status_code

    headers = request.headers
    if 'Authorization' in headers:
        token = headers['Authorization'].split(' ')[1]
        decoded_token = decode_token(token)

        # user_id = decoded_token['user_details']['id']
        amount = discounts_response.json()

        user = UserPayments.query.filter_by(id=user_id).first()
        if user is None:
            user = UserPayments(id=user_id, funds=0)
            db.session.add(user)
            # db.session.commit()
            
        # print ("Amount:", amount)
        transaction = Transaction(date=datetime.now(),
                                  amount=amount,
                                  user=user,
                                  completed=True)
        db.session.add(transaction)
        db.session.commit()
        return transaction_to_json(transaction), 200
    else:
        return {'message': 'Pay was not successful'}, 400


connexion_app = connexion.App(__name__, specification_dir="./config/")
app = connexion_app.app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
connexion_app.add_api("api.yml")

register_to_consul()

from models import PaymentMethods, UserPayments, Transaction, PayPal, CreditCards, MethodType, CardType
from functions import *

if __name__ == '__main__':
    connexion_app.run(port=5000, debug=True)
