from flask import Flask, redirect, render_template, url_for, request, Response, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_testing import TestCase
from flask_mail import Mail, Message
from random import randrange
import random
import os
import six
import json
from sqlalchemy.orm import relationship
from sqlalchemy.orm import session as sql_session
import requests
from application import app, db
from application.models import users, accounts


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/currencyexchange', methods=['GET', 'POST'])
def currencyexchange():
    if 'email' not in session:
        return redirect(url_for('home'))
    
    if request.method == "POST":
        # Getting values from form
        fromcurrency = request.form['fromcurrency'].upper()
        tocurrency = request.form['tocurrency'].upper()
        amount = request.form['amountToConvert']
        amountfloat = float(amount)
        currencies = ["usd", "eur", "gbp"]
        insufficientFunds = True
        
        if fromcurrency == "GBP":
            accountno = session['gbpaccountno']
        if fromcurrency == "EUR":
            accountno = session['euraccountno']
        if fromcurrency == "USD":
            accountno = session['usdaccountno']

        if tocurrency == "GBP":
            toaccountno = session['gbpaccountno']
        if tocurrency == "EUR":
            toaccountno = session['euraccountno']
        if tocurrency == "USD":
            toaccountno = session['usdaccountno']
        
        account = accounts.query.get(accountno)
        print(account.balance)

        if amountfloat > account.balance:
            print("Insufficient funds, please deposit more money or select a different currency.")
        else:
            insufficientFunds = False
            access_key = 'access_key=ad01d5e835ac2f8a2d63ed14c6183b74&base=' + fromcurrency
            response = requests.get('http://api.exchangeratesapi.io/v1/latest', params=access_key)
            print(response)
            print(response.json())
            print(tocurrency)
            data = response.json()
            exchangerate = data['rates'][tocurrency]
            print(exchangerate)
            valueinnewcurrency = amountfloat * exchangerate
            valueinnewcurrencyfinal = str(round(valueinnewcurrency, 2))
            print(valueinnewcurrency)
            # Subtracting money used in conversion from old account balance
            oldbal = account.balance - amountfloat
            oldbalfinal = float(round(oldbal, 2))
            account.balance = oldbalfinal
            db.session.commit()
            toaccount = accounts.query.get(toaccountno)
            originalbal = toaccount.balance
            # Setting new account balance for other currency
            toaccount.balance = float(originalbal) + float(valueinnewcurrencyfinal)
            db.session.commit()
            session['{0}balance'.format(fromcurrency)] = account.balance
            session['{0}balance'.format(tocurrency)] = toaccount.balance

        if insufficientFunds == True:
            flash('Insufficient funds, please deposit more money or select a different currency.')


    return render_template('currencyexchange.html')

@app.route('/deposit', methods=['GET', 'POST'])
def depositmoney():
    if 'email' not in session:
        return redirect(url_for('home'))

    if request.method == "POST":
        amount = request.form['amountToDeposit']
        depositcurrency = request.form['depositcurrency']
        print(depositcurrency)
        print(amount)

        if depositcurrency == "gbp":
            accountno = session['gbpaccountno']
        if depositcurrency == "eur":
            accountno = session['euraccountno']
        if depositcurrency == "usd":
            accountno = session['usdaccountno']

        # Query to DB using account number
        account = accounts.query.get(accountno)
        bal = account.balance
        newbal = float(bal) + float(amount)
        newbalfinal = float(round(newbal, 2))
        account.balance = newbalfinal
        db.session.commit()
        session['{0}balance'.format(depositcurrency)] = account.balance

    return render_template('depositmoney.html')


@app.route('/withdraw', methods=['GET', 'POST'])
def withdrawmoney():
    if 'email' not in session:
        return redirect(url_for('home'))

    if request.method == "POST":
        amount = request.form['amountToWithdraw']
        withdrawcurrency = request.form['withdrawcurrency']
        print(withdrawcurrency)
        print(amount)

        if withdrawcurrency == "gbp":
            accountno = session['gbpaccountno']
        if withdrawcurrency == "eur":
            accountno = session['euraccountno']
        if withdrawcurrency == "usd":
            accountno = session['usdaccountno']

        # Query to DB using account number
        account = accounts.query.get(accountno)
        bal = account.balance
        if float(bal) >= float(amount):
            newbal = float(bal) - float(amount)
            newbalfinal = float(round(newbal, 2))
            account.balance = newbalfinal
            db.session.commit()
            session['{0}balance'.format(withdrawcurrency)] = account.balance
        else:
            flash('Not enough funds to withdraw.', 'error')

    return render_template('withdrawmoney.html')

@app.route('/transfer', methods=['GET', 'POST'])
def transfermoney():
    if 'email' not in session:
        return redirect(url_for('home'))

    if request.method == "POST":
        amount = request.form['amountToTransfer']
        transfercurrency = request.form['transfercurrency']
        targetaccountno = request.form['transferto']
        print(transfercurrency)
        print(amount)

        if transfercurrency == "gbp":
            accountno = session['gbpaccountno']
        if transfercurrency == "eur":
            accountno = session['euraccountno']
        if transfercurrency == "usd":
            accountno = session['usdaccountno']

        # Query to DB using account number
        account = accounts.query.get(accountno)
        bal = account.balance
        if float(bal) >= float(amount):
            newbal = float(bal) - float(amount)
            newbalfinal = float(round(newbal, 2))
            account.balance = newbalfinal
            db.session.commit()
            session['{0}balance'.format(transfercurrency)] = account.balance

            transfertoaccount = accounts.query.get(targetaccountno)
            bal2 = transfertoaccount.balance
            newbal2 = float(bal2) + float(amount)
            newbalfinal2 = float(round(newbal2, 2))
            transfertoaccount.balance = newbalfinal2
            db.session.commit()
        else:
            flash('Not enough funds to withdraw.', 'error')

    return render_template('transfermoney.html')

@app.route('/myaccount')
def myaccount():
    if 'email' not in session:
        return redirect(url_for('home'))

    gbpaccountno = session['gbpaccountno']
    # Query to DB using account number
    gbpaccount = accounts.query.get(gbpaccountno)
    gbpbalance = gbpaccount.balance
    session['gbpbalance'] = gbpbalance

    euraccountno = session['euraccountno']
    # Query to DB using account number
    euraccount = accounts.query.get(euraccountno)
    eurbalance = euraccount.balance
    session['eurbalance'] = eurbalance

    usdaccountno = session['usdaccountno']
    # Query to DB using account number
    usdaccount = accounts.query.get(usdaccountno)
    usdbalance = usdaccount.balance
    session['usdbalance'] = usdbalance

    return render_template('myaccount.html')


@app.route('/latestrates')
def latestrates():

    fromcurrency = "gbp"
    access_key = 'access_key=ad01d5e835ac2f8a2d63ed14c6183b74&base=' + fromcurrency
    response = requests.get('http://api.exchangeratesapi.io/v1/latest', params=access_key)
    print(response)
    data = response.json()
    gbpeur = data['rates']['EUR']
    gbpusd = data['rates']['USD']
    session['gbpeur'] = gbpeur
    session['gbpusd'] = gbpusd

    fromcurrency = "eur"
    access_key = 'access_key=ad01d5e835ac2f8a2d63ed14c6183b74&base=' + fromcurrency
    response = requests.get('http://api.exchangeratesapi.io/v1/latest', params=access_key)
    print(response)
    data = response.json()
    eurgbp = data['rates']['GBP']
    eurusd = data['rates']['USD']
    session['eurgbp'] = eurgbp
    session['eurusd'] = eurusd

    fromcurrency = "usd"
    access_key = 'access_key=ad01d5e835ac2f8a2d63ed14c6183b74&base=' + fromcurrency
    response = requests.get('http://api.exchangeratesapi.io/v1/latest', params=access_key)
    print(response)
    data = response.json()
    usdeur = data['rates']['EUR']
    usdgbp = data['rates']['GBP']
    session['usdeur'] = usdeur
    session['usdgbp'] = usdgbp


    return render_template('latestrates.html')


@app.route('/logout')
def logout():
    if 'email' not in session:
        return redirect(url_for('home'))
    
    session.pop('email', None)
    return render_template('home.html')

@app.route('/delete')
def deleteuser():
    if 'email' not in session:
        return redirect(url_for('home'))
    
    useremail = session['email']
    user = users.query.filter_by(email=useremail).first()
    gbpaccount = accounts.query.filter_by(fk_user_id=user.id).limit(3)[0]
    euraccount = accounts.query.filter_by(fk_user_id=user.id).limit(3)[1]
    usdaccount = accounts.query.filter_by(fk_user_id=user.id).limit(3)[2]
    
    db.session.delete(gbpaccount)
    db.session.delete(euraccount)
    db.session.delete(usdaccount)
    db.session.delete(user)
    db.session.commit()
    session.pop('email', None)
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'email' in session:
        return redirect(url_for('home'))

    if request.method == "POST":
        emailform = request.form['emailinput']
        securecode = request.form['securecode']

        user = users.query.filter_by(email=emailform).first()
        gbpaccount = accounts.query.filter_by(fk_user_id=user.id).limit(3)[0]
        euraccount = accounts.query.filter_by(fk_user_id=user.id).limit(3)[1]
        usdaccount = accounts.query.filter_by(fk_user_id=user.id).limit(3)[2]
        print(user.securitycode)
        if user.email == emailform:
            print('email true')
            if user.securitycode == securecode:
                print('seucre code true')
                # Adding user to session
                session['email'] = emailform
                session['firstname'] = user.firstname
                session['lastname'] = user.surname
                session['dob'] = user.dob

                session['gbpbalance'] = gbpaccount.balance
                session['gbpaccountno'] = gbpaccount.accountno

                session['eurbalance'] = euraccount.balance
                session['euraccountno'] = euraccount.accountno

                session['usdbalance'] = usdaccount.balance
                session['usdaccountno'] = usdaccount.accountno
                return redirect(url_for('home'))
        else:
            flash('Email or secure code entered incorrect', 'error')
            return redirect(url_for('login'))       
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'email' in session:
        return redirect(url_for('home'))

    if request.method == "POST":
        # Data validation
        if not request.form['firstname'] or not request.form['surname'] or not request.form['emailinput'] or not request.form['securecode']:
            flash('Please enter all required details', 'error')
        else:
            user = users(firstname = request.form['firstname'], surname = request.form['surname'], email = request.form['emailinput'], dob = request.form['dob'], securitycode = request.form['securecode'])
            
            db.session.add(user)
            db.session.commit()
            
            # Generating account number for user's GBP account
            accountnumber = '0'
            for x in range(0, 5):
                number = random.randint(0,9)
                accountnumber = accountnumber + str(number)
            print(accountnumber)
            banksortcode = 783929
            userid = user.id
            gbpaccount = accounts(accountno = accountnumber, currency = "GBP", sortcode = banksortcode, balance = 0, fk_user_id = userid)

            # Generating account number for user's EUR account
            accountnumber2 = '0'
            for x in range(0, 5):
                number = random.randint(0,9)
                accountnumber2 = accountnumber2 + str(number)
            print(accountnumber2)
            euraccount = accounts(accountno = accountnumber2, currency = "EUR", sortcode = banksortcode, balance = 0, fk_user_id = userid)

            # Generating account number for user's USD account
            accountnumber3 = '0'
            for x in range(0, 5):
                number = random.randint(0,9)
                accountnumber3 = accountnumber3 + str(number)
            print(accountnumber3)
            usdaccount = accounts(accountno = accountnumber3, currency = "USD", sortcode = banksortcode, balance = 0, fk_user_id = userid)


            db.session.add(gbpaccount)
            db.session.add(euraccount)
            db.session.add(usdaccount)
            db.session.commit()
            session['sortcode'] = banksortcode
            session['gbpaccountno'] = accountnumber
            session['euraccountno'] = accountnumber2
            session['usdaccountno'] = accountnumber3
            
            # Emailing user
            #app.config['MAIL_SERVER'] = 'smtp.gmail.com'
            #app.config['MAIL_PORT'] = 465
            #app.config['MAIL_PASSWORD'] = ''
            #app.config['MAIL_USERNAME'] = 'andrei.chirovici@gmail.com'
            #app.config['MAIL_USE_TLS'] = False
            #app.config['MAIL_USE_SSL'] = True
            #mail = Mail(app)
            #msg = Message("Guess The Language Registration", sender="andrei.chirovici@gmail.com", recipients=[request.form['emailinput']])
            #msg.body = "Hello, welcome to guess the language! Enjoy playing!"
            #mail.send(msg)
            
            flash('User registration successful. Please login using your details.')
            return redirect(url_for('login'))

    return render_template('register.html')