from pydantic import BaseModel
from fastapi import FastAPI
from threading import Thread
import asyncio
import uvicorn
import time
import pika
import os

app = FastAPI()

PORT = os.environ.get("APPLICATION_PORT", "8080")
RABBIT_MQ_URL = os.environ.get("RABBIT_MQ_URL", "127.0.0.1")
RABBIT_MQ_PORT = os.environ.get("RABBIT_MQ_PORT", "5672")
RABBIT_CHANEL_NAME = os.environ.get("RABBIT_MQ_CHANNEL", "usernames")
RABBIT_MQ_FULL_URL = os.environ.get(
    "RABBIT_MQ_FULL_URL", "amqp://localhost:5672")

connection = pika.BlockingConnection(
    pika.URLParameters(RABBIT_MQ_FULL_URL))

channel = connection.channel()
channel.queue_declare(queue=RABBIT_CHANEL_NAME)


def closeConnection():
    print("Closing RabbitMq connection!")
    connection.close()


def sendAmaqpMessage(message):
    # Pause simulation
    time.sleep(5)
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
        Thread(target=sendAmaqpMessage, args=(username, )).start()
        return {"username": body.username, "success": True}
    except Exception as e:
        print(e)
        return {"message": e, "status": False}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(PORT))
