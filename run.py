from flask import Flask
import twilio.twiml

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def hello():
    """Respond to incoming requests."""
    resp = twilio.twiml.Response()
    
    with resp.gather(numDigits=1, action=url_for('menu'), method="POST") as g:
        g.play(url="http://howtodocs.s3.amazonaws.com/et-phone.mp3", loop=3)

    return twiml(resp)

@app.route('/fizz', methods=['POST'])
def fizz():
    selected_option = request.form['Digits']
    
    resp.say("you entered " + selected_option);

    return twiml(resp)




if __name__ == "__main__":
    app.run(debug=True)