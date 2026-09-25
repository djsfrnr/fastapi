import os
from fastapi import FastAPI, Request, Response

app = FastAPI()

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")


@app.get("/")
def root():
    return {
        "status": "online",
        "name": "Alberto AI",
        "version": "0.1"
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


@app.post("/webhook")
async def receive_webhook(request: Request):
    payload = await request.json()

    print("Instagram webhook received:")
    print(payload)

    return {"status": "ok"}
