from flask import Flask, request, render_template
import twilio.twiml
from twilio.rest import TwilioRestClient

account_sid = "AC78494ca3414bae8d75f682eb596a6fbb"
auth_token = "d4c4cf67ee7e13c86169026fe5fdc412"
url_path = "https://moseleyfizz.herokuapp.com/call"
phone = "+13158025153"

client = TwilioRestClient(account_sid, auth_token)

app = Flask(__name__)

@app.route('/<string:page_name>/')
def render_static(page_name):
    return render_template('%s.html' % page_name)

@app.route("/call", methods=['GET', 'POST'])
def hello():
    """Respond to incoming requests."""
    resp = twilio.twiml.Response()
    
    with resp.gather(finishOnKey="#", action='/fizz', method="POST") as g:
        g.say("please enter a number followed by pound")

    return str(resp)

@app.route('/fizz', methods=['POST'])
def fizz():
    resp = twilio.twiml.Response()
    selected_option = request.values['Digits']
    n = int(selected_option)
    ret=""
    for i in range(1, n+1):
        if(i%3==0):
            ret += "Sammy "
        if(i%5==0):
            ret += "loves you "
        if(i%3!=0 or i%5!=0):
            ret += str(i) + " "

    resp.say(ret)

    return str(resp)

@app.route('/make_call', methods=['POST'])
def make_call():
    call = client.calls.create(url=url_path,
    to=request.values['phone'],
    from_=phone)




if __name__ == "__main__":
    app.run(debug=True)