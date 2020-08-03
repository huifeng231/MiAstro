import json
import pickle
import uuid

import asyncio_redis
import asyncio_redis.connection
import asyncio_redis.protocol
# import dotenv
import os

# dotenv.load_dotenv()

async def create_connection_pool():
    return await asyncio_redis.Pool.create(host="127.0.0.1", port=6379,
                                           poolsize=5,db=15)


async def subscribe_channel(channel):
    connection = await create_connection_pool()
    subscription = await connection.start_subscribe()
    await subscription.subscribe(['Channel:{}'.format(channel)])
    return subscription


async def unsubscibe_channel(subscription: asyncio_redis.protocol.Subscription, channel):
    await subscription.unsubscribe(['Channel:{}'.format(channel)])


async def receive_message(subscription: asyncio_redis.protocol.Subscription):
    return await subscription.next_published()


async def send_message(channel, message):
    connection = await create_connection_pool()

    msg_id = uuid.uuid1().hex

    message = {"msg_id": msg_id, "msg_body": message}

    _channel = "message:{}".format(channel)
    _message = json.dumps(message)
    await connection.publish(_channel, _message)
    connection.close()
    return msg_id


async def broadcast_message(db, channel, msg_body):
    """
    广播消息
    :param channel:
    :param msg_body:
    :return:
    """
    msg_id = uuid.uuid1().hex

    message = {"msg_id": msg_id, "msg_body": msg_body}

    _channel = "message:{}".format(channel)
    _message = pickle.dumps(message)

    await db.publish(_channel, _message)

    return msg_id
