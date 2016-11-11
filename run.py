from flask import Flask, request, render_template, url_for, redirect, abort
import twilio.twiml
import os
from twilio.rest import TwilioRestClient
from twilio.util import RequestValidator
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.sql import update
from CallRecord import CallRecord
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta

sched = BackgroundScheduler()
sched.start()

account_sid = "AC78494ca3414bae8d75f682eb596a6fbb"
auth_token = "d4c4cf67ee7e13c86169026fe5fdc412"
url_path = "https://moseleyfizz.herokuapp.com/"
phone = "+13158025153"

client = TwilioRestClient(account_sid, auth_token)
validator = RequestValidator(auth_token)

app = Flask(__name__)
from CallRecord import db


import logging

log = logging.getLogger('apscheduler.executors.default')
log.setLevel(logging.INFO)  # DEBUG

fmt = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
h = logging.StreamHandler()
h.setFormatter(fmt)
log.addHandler(h)

#validates Twilio specific methods (default True right now, problem with X-Twilio-Signature)
def validate(req):
    return True;
    if not 'X-Twilio-Signature' in req.headers:
        return True
    return validator.validate(req.url_root, {x:str(req.values[x]) for x in sorted(req.values.keys())}, req.headers['X-Twilio-Signature'])

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/<string:page_name>/')
def render_static(page_name):
    return render_template('%s' % page_name)

#method for input call - if user initiates call
@app.route("/call/", methods=['GET', 'POST'])
def inputcall():
    if not validate(request):
        return abort(401)
    call = CallRecord({'phone': request.values['From']})
    db.session.add(call)
    db.session.commit()
    idn = call.idn
    resp = twilio.twiml.Response()
    with resp.gather(finishOnKey="#", action=url_path+'fizz/'+str(idn)+"/", method="POST") as g:
        for i in range(0, 3):
            g.say("please enter a number followed by pound")
            g.pause(length=3)    
        
    resp.say("hanging up now")
    return str(resp)

#method for output call - my app initiates call
#idn is primary key for CallRecord
@app.route("/call/<idn>/", methods=['GET', 'POST'])
def hello(idn):
    if not validate(request):
        return abort(401)

   #if the record doesn't exist, redirect as new call
    if(db.session.query(CallRecord).get(int(idn))==None): 
        return redirect(url_for('inputcall'))

    resp = twilio.twiml.Response()
    with resp.gather(finishOnKey="#", action=url_path+'fizz/'+str(idn)+"/", method="POST") as g:
        for i in range(0, 3):
            g.say("please enter a number followed by pound")
            g.pause(length=3)    
        
    resp.say("hanging up now")
    return str(resp)

#fizz buzz implementation, after user presses number
#idn is pimary key for Call Record
@app.route('/fizz/<idn>/', methods=['GET', 'POST'])
def fizz(idn):
    if not validate(request):
        return redirect(url_for('index'))
    rec = db.session.query(CallRecord).get(int(idn))
    
    #if the record doesn't exist, redirect as new call
    if(rec==None): 
        return redirect(url_for('inputcall'))

    db.session.query(CallRecord).filter(CallRecord.idn == idn).update({"completed": True})
    resp = twilio.twiml.Response()
    selected_option = 1 #default
    if 'Digits' in request.values:
        selected_option = request.values['Digits']
    
    n=1
    if(rec.number!=-1):
        n=rec.number
    else: #check the selected number is number
        n=int(selected_option)
        db.session.query(CallRecord).filter(CallRecord.idn == int(idn)).update({'number': n})
        db.session.commit()
    ret=""
    for i in range(1, n+1):
        if(i%3==0):
            ret += "Fizz " #fizzy fizz fizz fizz
        if(i%5==0):
            ret += "Buzz " #buzzy buzz buzz buzz
        if(i%3!=0 and i%5!=0):
            ret += str(i) + " "

    resp.say(ret)
    return str(resp)


# @app.route('/make_call/', methods=['POST'])
# def make_call():
#     call = client.calls.create(url=url_path,
#     to=request.values['phone'],
#     from_=phone)
#     return 'sucess'

#schedule call with delay
def scheduledCall(idn):
    call = db.session.query(CallRecord).get(int(idn))
    if(call==None):
        return
    print "making call " + str(call.idn)
    client.calls.create(url=url_path+"call/"+str(call.idn)+"/", to=call.phone, from_=phone)
    db.session.commit()

#replay call
def replayCall(idn):
    call = db.session.query(CallRecord).get(int(idn))
    if(call==None):
        return
    print "making replay call " + str(call.idn)
    if call.number!=-1:
        client.calls.create(url=url_path+"fizz/"+str(call.idn)+"/", to=call.phone, from_=phone)
    else:
        client.calls.create(url=url_path+"call/"+str(call.idn)+"/", to=call.phone, from_=phone)
    db.session.commit()

#add call
@app.route('/add/', methods=['POST'])
def add():
    if not 'phone' in request.values:
        return "-1"
    if not request.values['delay'].isdigit():
        return "-1"

    call = CallRecord(request.values)
    db.session.add(call)
    db.session.commit()
    time = call.time + timedelta(seconds=call.delay)
    sched.add_job(scheduledCall, run_date=time, args=[call.idn])
    return str(call.idn)


#remove call record, call won't be placed if call record is deleted
@app.route('/delete/<idn>/', methods=['POST'])
def remove(idn):
    call = CallRecord.query.get(int(idn))
    if call is None:
        return 'error'
    else:
        db.session.delete(call)
        db.session.commit()
    return 'success'

#replay call immediately
@app.route('/replay/<idn>/', methods=['POST'])
def replay(idn):
    call = CallRecord.query.get(int(idn))
    new_call = CallRecord({'phone':call.phone,'number':call.number})
    db.session.add(new_call)
    db.session.commit()
    replayCall(new_call.idn)
    return 'success'

#list calls in json (used for web front end)
@app.route('/listcalls/', methods=['GET'])
def listcalls():
    ls = CallRecord.query.order_by(CallRecord.idn)
    r = '['
    for i in range(0, ls.count()):
        r += str(ls[i]) + ','
    r = r[:-1] + ']'
    return r




if __name__ == "__main__":
    app.run(debug=True)