import os
from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Enqueue
from twilio.twiml.voice_response import Dial

app = Flask(__name__)


@app.route("/answer", methods=["GET", "POST"])
def answer_call():
    """Handle incoming call and place the caller in a queue."""
    resp = VoiceResponse()

    resp.play(os.environ["WELCOME_URL"])

    resp.enqueue("support_queue", wait_url="/hold")

    return str(resp)


@app.route("/hold", methods=["GET", "POST"])
def hold_music():
    """Return hold music or looping message while the caller is in the queue."""
    resp = VoiceResponse()

    resp.play(os.environ["HOLD_MUSIC_URL"])

    return str(resp)


@app.route("/agent", methods=["GET", "POST"])
def agent_connect():
    """Endpoint for an agent to connect to the call queue."""
    resp = VoiceResponse()
    dial = Dial()

    dial.queue("support_queue")
    resp.append(dial)
    return str(resp)


if __name__ == "__main__":
    app.run(debug=True, port=3000)
