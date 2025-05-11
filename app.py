import os
from flask import Flask, request, jsonify
from twilio.twiml.voice_response import VoiceResponse, Enqueue
from twilio.twiml.voice_response import Dial
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from flask_cors import CORS

app = Flask(__name__)
CORS(app, supports_credentials=True)
CORS(app, resources=r"/queue-size")

twilio_client = Client(
    os.environ.get("TWILIO_ACCOUNT_SID"), os.environ.get("TWILIO_AUTH_TOKEN")
)

QUEUE_NAME = "support_queue"


def get_or_create_queue():
    """Get the queue if it exists, create it if it doesn't."""
    try:
        queues = twilio_client.queues.list()
        for queue in queues:
            if queue.friendly_name == QUEUE_NAME:
                return queue

        queue = twilio_client.queues.create(friendly_name=QUEUE_NAME)
        return queue
    except TwilioRestException as e:
        raise e


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


@app.route("/queue-size", methods=["GET"])
def get_queue_size():
    """Get the current number of callers in the support queue."""
    try:
        queue = get_or_create_queue()
        return jsonify(
            {"queue_size": queue.current_size, "queue_name": queue.friendly_name}
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=3001)
