import os
from flask import Flask, request, jsonify
from twilio.twiml.voice_response import VoiceResponse, Enqueue
from twilio.twiml.voice_response import Dial
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from flask_cors import CORS
from flask import url_for

app = Flask(__name__)
CORS(app, supports_credentials=True)
CORS(app, resources=r"/queue-size")

twilio_client = Client(
    os.environ.get("TWILIO_ACCOUNT_SID"), os.environ.get("TWILIO_AUTH_TOKEN")
)


@app.route("/answer", methods=["POST"])
def answer_call():
    resp = VoiceResponse()
    resp.play(os.environ["WELCOME_URL"])
    
    return str(resp)


if __name__ == "__main__":
    app.run(debug=True, port=3001)
