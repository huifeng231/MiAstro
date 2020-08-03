#!/usr/bin/env python
import asyncio
import os

from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient

# from config import CONFIG
from utils.tools import singleton


@singleton
class MotorBase:
    """
    更改mongodb连接方式 单例模式下支持多库操作
    About motor's doc: https://github.com/mongodb/motor
    """
    _db = {}
    _collection = {}
    env_data = os.environ
    MONGODB = dict(
        MONGO_HOST=env_data.get("ACLIENTS_MONGO_HOST"),
        MONGO_PORT=int(env_data.get("ACLIENTS_MONGO_PORT")),
        MONGO_USERNAME=env_data.get("ACLIENTS_MONGO_USERNAME"),
        MONGO_PASSWORD=env_data.get("ACLIENTS_MONGO_PASSWD"),
        DATABASE=env_data.get("ACLIENTS_MONGO_DBNAME"),
    )

    def __init__(self, loop=None):
        self.motor_uri = ''
        self.loop = loop or asyncio.get_event_loop()

    def client(self, db):
        # motor
        self.motor_uri = 'mongodb://{account}{host}:{port}/{database}'.format(
            account='{username}:{password}@'.format(
                username=self.MONGODB['MONGO_USERNAME'],
                password=self.MONGODB['MONGO_PASSWORD']) if self.MONGODB['MONGO_USERNAME'] else '',
            host=self.MONGODB['MONGO_HOST'] if self.MONGODB['MONGO_HOST'] else 'localhost',
            port=self.MONGODB['MONGO_PORT'] if self.MONGODB['MONGO_PORT'] else 27017,
            database=db)
        return AsyncIOMotorClient(self.motor_uri, io_loop=self.loop)

    def get_db(self, db=MONGODB['DATABASE']):
        """
        Get a db instance
        :param db: database name
        :return: the motor db instance
        """
        if db not in self._db:
            self._db[db] = self.client(db)[db]

        return self._db[db]

    def get_collection(self, db_name, collection):
        """
        Get a collection instance
        :param db_name: database name
        :param collection: collection name
        :return: the motor collection instance
        """
        collection_key = db_name + collection
        if collection_key not in self._collection:
            self._collection[collection_key] = self.get_db(db_name)[collection]

        return self._collection[collection_key]


if __name__ == '__main__':
    def async_callback(func, **kwargs):
        """
        Call the asynchronous function
        :param func: a async function
        :param kwargs: params
        :return: result
        """
        loop = asyncio.get_event_loop()
        task = asyncio.ensure_future(func(**kwargs))
        loop.run_until_complete(task)
        return task.result()


    motor_base = MotorBase()
    motor_db = motor_base.get_db()


    async def insert(data):
        print(data)
        await motor_db.test.save(data)


    async_callback(insert, data={'hi': 'owllook'})
