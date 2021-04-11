import connexion
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

def hello_world(name: str) -> str:
    return 'Hello World! {name}'.format(name=name)
def findAllTransactions():
    transactions = db.session.query(Transaction)
    if transactions:
        return transactions
    else:
        return {'error'},404
def findTransactionsByUserID(user_id):
    transaction = db.session.query(Transaction).filter_by(user_id=user_id).first()
    if transaction:
       return transaction
    else:
        return {'error' : '{} not found'.format(user_id)},404
def editTransaction(id,transaction_body):
    transaction = db.session.query(Transaction).filter_by(id=id).first()
    if transaction:
        transaction.user_id = transaction_body['user_id']
        transaction.amount= transaction_body['amount']
        transaction.completed= transaction_body['completed']
        transaction.date=datetime.now()
        db.session.add(transaction)
        db.session.commit()
        return transaction
    else:
        return {'error not found'},404
def saveTransaction(transaction_body):
    transaction = Transaction(id=transaction_body['id'],date=datetime.now(),amount=transaction_body['amount'],user_id=transaction_body['user_id'])
    db.session.add(transaction)
    db.session.commit()
def saveUserPaymentMethod(user_payment_method):
    payment_method=db.session.query.filter_by(id=user_payment_method['payment_method_id']).first()
    if payment_method:
        user = UserPayments(id=user_payment_method['id'],payment_methods=payment_method)
        db.session.add(user)
        db.session.commit()
        return user
    else:
        return {'error not found'},404
def findAllUsersPaymentsMethods():
    paymentMethods = db.session.query(UserPayments)
    if paymentMethods:
        return paymentMethods
    else:
        return {'error not found'},404
def findUserPaymentMethodById(id):
    payment_method = db.session.query(UserPayments).filter_by(id=id).first()
    if payment_method:
        return payment_method
    else:
        return {'error not found'},404
def deleteUserPaymentMethodById(id):
    payment_method = db.session.query(UserPayments).filter_by(id=id).first()
    if payment_method:
        db.session.delete(payment_method)
        db.session.commit()
        return payment_method
    else:
        return {'error not found'},404



connexion_app = connexion.App(__name__, specification_dir="./config/")
app = connexion_app.app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
connexion_app.add_api("api.yml")

from models import PaymentMethods, UserPayments, Transaction, PayPal, CreditCards

if __name__ == '__main__':
    connexion_app.run(port=5000, debug=True)
    
