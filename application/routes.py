from flask import Flask, redirect, render_template, url_for, request, Response, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_testing import TestCase
from flask_mail import Mail, Message
from random import randrange
import random
import os
import six
from sqlalchemy.orm import relationship
from sqlalchemy.orm import session as sql_session
from application import app, db
from application.models import users, accounts

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')

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
    account = accounts.query.filter_by(fk_user_id=user.id).first()
    
    print(account)
    db.session.delete(account)
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
            
            flash('Record was successfully added')
            return redirect(url_for('login'))

    return render_template('register.html')