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

QUEUE_NAME = "support_queue"

MAX_QUEUE_SIZE = 10


def get_or_create_queue():
    """Get the queue if it exists, create/update it if it doesn't or size differs."""
    try:
        for queue in twilio_client.queues.list():
            if queue.friendly_name == QUEUE_NAME:
                if queue.max_size != MAX_QUEUE_SIZE:
                    twilio_client.queues(queue.sid).update(max_size=MAX_QUEUE_SIZE)
                return queue

        return twilio_client.queues.create(
            friendly_name=QUEUE_NAME, max_size=MAX_QUEUE_SIZE
        )
    except TwilioRestException as e:
        raise


@app.route("/answer", methods=["POST"])
def answer_call():
    resp = VoiceResponse()
    resp.play(os.environ["WELCOME_URL"])

    hold_url = url_for("hold_music", _external=True)
    action_url = url_for("enqueue_status", _external=True)

    resp.enqueue(QUEUE_NAME, wait_url=hold_url, action=action_url, method="POST")
    return str(resp)


@app.route("/enqueue_status", methods=["POST"])
def enqueue_status():
    result = request.values.get("QueueResult")
    resp = VoiceResponse()

    if result == "queue-full":
        resp.say("Sorry, our queue is full. Please try again later.")
        resp.hangup()
    else:
        resp.say("Thanks for waiting.")
        resp.hangup()

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
