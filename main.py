import os
import requests

from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse

app = FastAPI()

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
INSTAGRAM_USER_ID = os.getenv("INSTAGRAM_USER_ID")


@app.get("/")
def root():
    return {
        "status": "online",
        "name": "Alberto AI",
        "version": "0.2"
    }


@app.get("/webhook")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN and challenge:
        return Response(
            content=challenge,
            media_type="text/plain",
            status_code=200
        )

    return Response(content="Forbidden", status_code=403)


def send_instagram_message(recipient_id: str, text: str):
    url = f"https://graph.instagram.com/v26.0/{INSTAGRAM_USER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {INSTAGRAM_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": text
        }
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=15
    )

    print("Instagram send status:", response.status_code)
    print("Instagram send response:", response.text)

    return response


@app.post("/webhook")
async def receive_webhook(request: Request):
    payload = await request.json()

    print("Instagram webhook received:")
    print(payload)

    try:
        entries = payload.get("entry", [])

        for entry in entries:
            messaging_events = entry.get("messaging", [])

            for event in messaging_events:
                sender_id = event.get("sender", {}).get("id")
                message = event.get("message", {})
                text = message.get("text")

                # Ignorar eventos sem texto
                if not sender_id or not text:
                    continue

                # Evitar responder às próprias mensagens do Alberto
                if str(sender_id) == str(INSTAGRAM_USER_ID):
                    continue

                # Evitar responder a mensagens eco
                if message.get("is_echo"):
                    continue

                print(f"Message from {sender_id}: {text}")

                send_instagram_message(
                    recipient_id=sender_id,
                    text="Demoraste."
                )

    except Exception as e:
        print("Webhook processing error:", str(e))

    return {"status": "ok"}


@app.get("/privacy", response_class=HTMLResponse)
def privacy():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Alberto AI Privacy Policy</title>
    </head>

    <body style="
        font-family: Arial, sans-serif;
        max-width: 800px;
        margin: 40px auto;
        padding: 0 20px;
        line-height: 1.6;
        color: #222;
    ">

        <h1>Alberto AI Privacy Policy</h1>

        <p>
            Alberto AI is an artificial intelligence-based digital character
            designed for conversation, entertainment and personalized interactions.
        </p>

        <h2>Information we process</h2>

        <p>
            We may process Instagram usernames, messages, conversation history,
            preferences and other information voluntarily provided when interacting
            with Alberto AI.
        </p>

        <h2>How information is used</h2>

        <p>
            Information may be used to provide conversations, maintain context,
            personalize responses, operate the service, manage subscriptions and
            improve the Alberto AI experience.
        </p>

        <h2>Artificial intelligence processing</h2>

        <p>
            Messages may be processed using third-party artificial intelligence,
            hosting, database and infrastructure providers when necessary to
            provide the service.
        </p>

        <h2>Data retention</h2>

        <p>
            We aim to retain only information reasonably necessary to operate
            Alberto AI. Users may request deletion of information associated
            with their interactions.
        </p>

        <h2>Data sharing</h2>

        <p>
            Alberto AI does not sell personal information. Information may be
            processed by technical providers required to operate the service.
        </p>

        <h2>User rights</h2>

        <p>
            Users may request access, correction or deletion of information
            associated with their use of Alberto AI.
        </p>

        <h2>Artificial character disclosure</h2>

        <p>
            Alberto is an artificial intelligence-generated fictional character
            and is not a real human individual.
        </p>

        <h2>Contact</h2>

        <p>
            For privacy-related requests, contact the Alberto AI administrator.
        </p>

        <p><strong>Last updated:</strong> September 2026</p>

    </body>
    </html>
    """


@app.get("/auth/callback")
def auth_callback():
    return {
        "status": "ok",
        "message": "Alberto AI Instagram login completed."
    }
