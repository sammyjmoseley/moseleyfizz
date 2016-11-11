from flask import Flask
import os
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)

class CallRecord(db.Model):
    idn = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime)       #time the request was made (or call recieved)
    phone = db.Column(db.String(20))    #phone number
    delay = db.Column(db.Integer)       #delay amount in seconds
    completed = db.Column(db.Boolean)   #boolean flag if call was made
    number = db.Column(db.Integer)      #number pressed, -1 if no record yet

    def __init__(self, arg):
        if not 'time' in arg:
            self.time = datetime.now()
        else: 
            self.time = arg['time']
        
        self.phone = arg['phone']

        if not 'delay' in arg:
            self.delay = 0
        else: 
            self.delay = int(arg['delay'])

        if not 'completed' in arg:
            self.completed = False
        else:
            self.completed = bool(arg['completed'])

        if not 'number' in arg:
            self.number=-1
        else:
            self.number = int(arg['number'])

    def __repr__(self):
        return '<id %r>' % self.idn

    def __str__(self):
        return "{"+ "\"id\" : "        + "\"" + str(self.idn)+ "\"" +\
               ","+ "\"time\" : "      + "\"" + str(self.time.strftime("%Y-%m-%d %H:%M:%S"))+ "\"" + \
               ","+ "\"phone\" : "     + "\"" + str(self.phone) + "\"" +\
               ","+ "\"delay\" : "     + str(self.delay)+\
               ","+ "\"completed\" : " + "\"" + str(self.completed)+ "\"" +\
               ","+ "\"number\" : "    + "\"" + str(self.number if self.number!= -1 else "##") + "\"" + "}"

db.create_all()
db.session.commit()