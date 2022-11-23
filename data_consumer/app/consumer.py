import pymongo
import pika
import os
import sys

RABBIT_MQ_URL = os.environ.get("RABBIT_MQ_URL", "localhost")
RABBIT_MQ_PORT = os.environ.get("RABBIT_MQ_PORT", "15672")
RABBIT_CHANEL_NAME = os.environ.get("RABBIT_MQ_CHANNEL", "usernames")
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://mongodb_container:27017/")
RABBIT_MQ_FULL_URL = "amqp://guest:guest@rabbitmq_service?heartbeat=600&blocked_connection_timeout=300"

MONGO_DB = "t_users"
MONGO_SCHEMA = "users"

mongoClient = pymongo.MongoClient(MONGO_URL)


def insertData(data):
    mydb = mongoClient[MONGO_DB]
    mycol = mydb[MONGO_SCHEMA]
    return mycol.insert_one(data)


def callback(ch, method, properties, body):
    print(" [x] Message received %r" % body)
    dataDecoded = body.decode('ascii')
    id = insertData({"username": dataDecoded})
    print(" [INFO] Inserted data... _id %r" % id)


def main():
    print(RABBIT_MQ_URL, " ", RABBIT_MQ_PORT)
    connection = pika.BlockingConnection(
        pika.URLParameters(RABBIT_MQ_FULL_URL))
    channel = connection.channel()
    channel.queue_declare(queue=RABBIT_CHANEL_NAME)
    channel.basic_consume(queue=RABBIT_CHANEL_NAME,
                          auto_ack=True, on_message_callback=callback)

    print(' [*] Waiting for messages. To exit press CTRL+C')

    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(' [!] Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
