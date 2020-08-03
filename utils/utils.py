#!/usr/bin/env python3
# coding=utf-8

"""
@author: guoyanfeng
@software: PyCharm
@time: 18-12-26 下午3:32
"""
import asyncio
import datetime
import decimal
import json
import multiprocessing
import pickle
import secrets
import string
import sys
import time
import uuid
import weakref
import logging
from collections import MutableMapping, MutableSequence
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager

import aioredis
import yaml
from bson import ObjectId
from sanic import request

from .exceptions import Error, FuncArgsError

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

__all__ = ("ignore_error", "verify_message", "wrap_async_func", "analysis_yaml", "gen_class_name", "objectid",
           "Singleton", "Cached", "gen_ident")

# 执行任务的线程池
pool = ThreadPoolExecutor(multiprocessing.cpu_count() * 10 + multiprocessing.cpu_count())


def gen_ident(ident_len=8):
    """
    获取随机的标识码以字母开头， 默认8个字符的长度
    Args:
    Returns:
    """
    ident_len = ident_len - 1
    alphabet = f"{string.ascii_lowercase}{string.digits}"
    ident = ''.join(secrets.choice(alphabet) for _ in range(ident_len))
    return f"{secrets.choice(string.ascii_lowercase)}{ident}"


@contextmanager
def ignore_error(error=Exception):
    """
    个别情况下会忽略遇到的错误
    Args:
    Returns:
    """
    # noinspection PyBroadException
    try:
        yield
    except error:
        pass


def verify_message(src_message: dict, message: list or dict):
    """
    对用户提供的message进行校验
    Args:
        src_message: 默认提供的消息内容
        message: 指定的消息内容
    Returns:
    """
    src_message = dict(src_message)
    message = message if isinstance(message, MutableSequence) else [message]
    required_field = {"msg_code", "msg_zh", "msg_en"}

    for msg in message:
        if isinstance(msg, MutableMapping):
            if set(msg.keys()).intersection(required_field) == required_field and msg["msg_code"] in src_message:
                src_message[msg["msg_code"]].update(msg)
    return src_message


async def wrap_async_func(func, *args, **kwargs):
    """
    包装同步阻塞请求为异步非阻塞
    Args:
        func: 实际请求的函数名或者方法名
        args: 函数参数
        kwargs: 函数参数
    Returns:
        返回执行后的结果
    """
    try:
        result = await asyncio.wrap_future(pool.submit(func, *args, **kwargs))
    except TypeError as e:
        raise FuncArgsError("Args error: {}".format(e))
    except Exception as e:
        raise Error("Error: {}".format(e))
    else:
        return result


def gen_class_name(underline_name):
    """
    由下划线的名称变为驼峰的名称
    Args:
        underline_name
    Returns:
    """
    return "".join([name.capitalize() for name in underline_name.split("_")])


def analysis_yaml(full_conf_path):
    """
    解析yaml文件
    Args:
        full_conf_path: yaml配置文件路径
    Returns:
    """
    with open(full_conf_path, 'rt', encoding="utf8") as f:
        try:
            conf = yaml.load(f, Loader=Loader)
        except yaml.YAMLError as e:
            print("Yaml配置文件出错, {}".format(e))
            sys.exit()
    return conf


def objectid():
    """
    Args:
    Returns:
    """
    return str(ObjectId())


class _Singleton(type):
    """
    singleton for class
    """

    def __init__(cls, *args, **kwargs):
        cls.__instance = None
        super().__init__(*args, **kwargs)

    def __call__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__call__(*args, **kwargs)
            return cls.__instance
        else:
            return cls.__instance


class _Cached(type):
    def __init__(cls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls.__cache = weakref.WeakValueDictionary()

    def __call__(cls, *args, **kwargs):
        cached_name = f"{args}{kwargs}"
        if cached_name in cls.__cache:
            return cls.__cache[cached_name]
        else:
            obj = super().__call__(*args, **kwargs)
            cls.__cache[cached_name] = obj  # 这里是弱引用不能直接赋值，否则会被垃圾回收期回收
            return obj


class Singleton(metaclass=_Singleton):
    pass


class Cached(metaclass=_Cached):
    pass

from sanic.response import json as json_response

logger = logging.getLogger("root")


def json_encoder(data):
    logger.info("Rjson %s" % data)
    return json_response(data, dumps=json.dumps,cls=DateEncoder)


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, decimal.Decimal):
            return str(obj.quantize(decimal.Decimal('0.00')))
        elif isinstance(obj, ObjectId):
            return str(obj)
        else:
            return json.JSONEncoder.default(self, obj)


#获取一个锁
# lock_name：锁定名称
# acquire_time: 客户端等待获取锁的时间
# time_out: 锁的超时时间
async def acquire_lock(redis_client, lock_name, acquire_time=10, time_out=10):
    """获取一个分布式锁"""
    identifier = str(uuid.uuid4())
    end = time.time() + acquire_time
    lock = "string:lock:" + lock_name
    logger.info("lock string:lock: %s identifier %s" % (lock_name, identifier))
    while time.time() < end:
        if await redis_client.setnx(lock, identifier):
            # 给锁设置超时时间, 防止进程崩溃导致其他进程无法获取锁
            await redis_client.expire(lock, time_out)
            return identifier
        elif not redis_client.ttl(lock):
            await redis_client.expire(lock, time_out)
        time.sleep(0.001)
    return False

#释放一个锁
async def release_lock(redis_client, lock_name, identifier):
    """通用的锁释放函数"""
    lock = "string:lock:" + lock_name
    logger.info("del lock string:lock: %s identifier %s" % (lock_name, identifier))
    pip = await redis_client.pipeline(True)
    while True:
        try:
            pip.watch(lock)
            lock_value = await redis_client.get(lock)
            if not lock_value:
                return True

            if lock_value.decode() == identifier:
                await pip.multi()
                await pip.delete(lock)
                await pip.execute()
                return True
            await pip.unwatch()
            break
        except:
            pass
    return False


class DistributedLock(object):
    """
    分布式锁,基于Redis的setNx特性实现
    name 请根据锁定的资源名称制定，不要随意使用相同的名称，避免相同的资源锁名
    """

    def __init__(self, rds_client, name, timeout=2, ex=10, slp=0.4):
        self.rds_client = rds_client
        self.name = "DistributedLock:" + name
        self.trys = timeout
        self.ex = ex
        self.slp = slp
        self.ts = time.time()

    def __enter__(self):
        locked = self._try_lock()
        if not locked:
            raise Exception("Distributed Lock Timeout.")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # self._release()
        pass

    async def _try_lock(self):
        """尝试得到锁，超时返回False"""
        rds = self.rds_client
        while True:
            locked = await rds.set(self.name, 1, ex=self.ex, nx=True)
            logger.info("1111111 %s" % rds.keys("*"))
            if locked:
                return True
            if time.time() - self.ts >= self.trys:
                return False
            time.sleep(self.slp or 1)

    async def _release(self):
        rds = self.rds_client
        await rds.delete(self.name)
        return True

    # @classmethod
    async def nx_lock(self, name, ex=10):
        """
        给资源上锁
        :param name:
        :param ex:
        :return: bool
        """
        rds = self.rds_client
        locked = await rds.set("NX_LOCK:{}".format(name), 1, ex=ex, nx=True)
        if locked:
            return True

        return False

    # @classmethod
    async def del_nx_lock(self, name):
        """
        删除资源锁
        :param name:
        """
        rds = self.rds_client
        await rds.delete("NX_LOCK:{}".format(name))


async def broadcast_message(rds_client, channel, msg_body):
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
    await rds_client.publish(_channel, _message)
    return msg_id


async def parse_user_ip(request, ip):
    url = 'http://ip-api.com/json/' + ip
    try:
        aio_req = request.app.aio_req
        response = await aio_req.async_post(url=url)
        response = response.json()
        response["res_code"] = 0
    except Exception as e:
        response = {"e": e, "res_code": 502}
    return response