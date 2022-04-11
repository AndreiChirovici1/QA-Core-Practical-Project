from flask import Flask, redirect, render_template, url_for, request, Response, session, flash
from flask_testing import TestCase
from flask_mail import Mail, Message
from random import randrange
import os
import six
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import session as sql_session
from sqlalchemy.ext.declarative import declarative_base
from os import getenv
from application import db

# Database

class users(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    firstname = db.Column(db.String(50))
    surname = db.Column(db.String(50))
    email = db.Column(db.String(100))
    dob = db.Column(db.String(15))
    securitycode = db.Column(db.String(100))  
    account = db.relationship('accounts', backref='users')

class accounts(db.Model):
    accountno = db.Column(db.Integer, primary_key = True)
    currency = db.Column(db.String(3))
    sortcode = db.Column(db.String(6))
    balance = db.Column(db.Float(10))
    fk_user_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)

def __init__(self, firstname, surname, email, dob, sortcode, securitycode, balance, currency, fk_user_id):
    self.firstname = firstname
    self.surname = surname
    self.dob = dob
    self.email = email
    self.sortcode = sortcode
    self.balance = balance
    self.currency = currency
    self.securitycode = securitycode
    self.fk_user_id = fk_user_id