from pydantic import BaseModel
from fastapi import FastAPI
import uvicorn
import pika
import os

app = FastAPI()

PORT = os.environ.get("APPLICATION_PORT", "8080")
RABBIT_MQ_URL = os.environ.get("RABBIT_MQ_URL", "127.0.0.1")
RABBIT_MQ_PORT = os.environ.get("RABBIT_MQ_PORT", "5672")
RABBIT_CHANEL_NAME = os.environ.get("RABBIT_MQ_CHANNEL", "usernames")
RABBIT_MQ_FULL_URL = "amqp://guest:guest@rabbitmq_service?heartbeat=600&blocked_connection_timeout=300"

connection = pika.BlockingConnection(
    pika.URLParameters(RABBIT_MQ_FULL_URL))

channel = connection.channel()
channel.queue_declare(queue=RABBIT_CHANEL_NAME)


def closeConnection():
    print("Closing RabbitMq connection!")
    connection.close()


def sendAmaqpMessage(message):
    channel.basic_publish(
        exchange='', routing_key=RABBIT_CHANEL_NAME, body=message)


class RequestBody(BaseModel):
    username: str


@app.get("/")
async def root():
    return {"message": "POST /api/username/"}


@app.post("/api/users/")
async def root(body: RequestBody):
    try:
        username = body.username
        sendAmaqpMessage(username)
        return {"username": body.username, "success": True}
    except Exception as e:
        print(e)
        return {"message": e, "status": False}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(PORT))
