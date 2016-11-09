from flask import Flask, request
import twilio.twiml

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
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
            ret += "Fizz "
        if(i%5==0):
            ret += "Buzz "
        if(i%3!=0 or i%5!=0):
            ret += str(i) + " "

    resp.say(ret)

    return str(resp)




if __name__ == "__main__":
    app.run(debug=True)