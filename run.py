from flask import Flask, request
import twilio.twiml

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def hello():
    """Respond to incoming requests."""
    resp = twilio.twiml.Response()
    
    with resp.gather(numDigits=1, action='/fizz', method="POST") as g:
        g.say("please enter a number")

    return str(resp)

@app.route('/fizz', methods=['POST'])
def fizz():
    resp = twilio.twiml.Response()
    selected_option = request.values['Digits']
    
    resp.say("you entered " + selected_option)

    return str(resp)




if __name__ == "__main__":
    app.run(debug=True)