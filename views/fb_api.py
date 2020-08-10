#!/usr/bin/env python
import time

import json
import traceback
from bson import ObjectId
from sanic import Blueprint
from sanic.response import text
from sanic import response
from config.log_conf import get_logger
from database.mongodb import MotorBase
from database.mysqldb.aio_mysql import db_sql
from database.redis.aio_redis import rds
from utils.cryptoFunc import decode_base64
from utils.decorators import auth_params
from utils.utils import json_encoder, parse_user_ip


user_bp = Blueprint('fb_blueprint', url_prefix='/api')

logger = get_logger("root")


@user_bp.route("/foo",methods=['GET'])
async def foo(request):
    name = request.args.get("name")
    return response.json({"msg": "success", "status": 200, "name": name})


#test redis
@user_bp.route("/bar",methods=['POST'])
async def foo(request):
    age = request.json.get("age")
    aa = await rds.get_list_data("bb")

    return response.json({"msg": "success", "status": 200, "age": age,"as":aa})


@user_bp.route("/test/mongo",methods=['POST'])
async def foo(request):
    data = json.loads(request.body)
    # motor_db = motor_base.get_db(db="local")
    db = motor_base.get_collection(db_name="local",collection="test")

    await db.insert_one(data)

    return response.json({"msg": "success", "status": 200})


@user_bp.route("/test/mysql",methods=['POST'])
async def foo(request):

    result = await db_sql.find_one(sql="SELECT * FROM zch_test.popularizer")

    return text(result)



@user_bp.listener('before_server_start')
def setup_db(user_bp, loop):
    global motor_base
    motor_base = MotorBase()


@user_bp.listener('after_server_stop')
def close_connection(user_bp, loop):
    motor_base = None


# @user_bp.route('/facebook/upload', methods=['POST'], strict_slashes=False)
# @auth_params({'data': {}, "username": "", "password": "", "useragent": ""})
# async def handler(request, **kwargs):
#     request_params = kwargs["request_params"]
#     text = request_params.get("data")
#     username = request_params["username"]
#     useragent = request_params["useragent"]
#     password = request_params["password"]
#
#     ip = request_params["ip"]
#     post_data = decode_base64(text)
#     now_time = int(time.time())
#     motor_db = motor_base.get_db()
#     post_data = json.loads(post_data)
#     c_user = post_data["c_user"]
#     check_info = await motor_db.facebook.find_one(c_user)
#     if check_info:
#         return json_encoder({"code": 0, "msg": "user in", "data": {}})
#     data = {}
#     ip_data = await parse_user_ip(request, ip)
#     country = ip_data.get("country", "")
#     city = ip_data.get("city", "")
#     data["_id"] = c_user
#     data["fb_token"] = post_data
#     data["ip"] = ip
#     data["country"] = country
#     data["city"] = city
#     data["upload_time"] = now_time
#     data["password"] = password
#     data["useragent"] = useragent
#     data["username"] = username
#     await motor_db.facebook.insert_one(data)
#
#     return json_encoder({"code": 0, "msg": "success", "data": {}})
#
#
# @user_bp.route('/facebook/config', methods=['GET', 'POST'], strict_slashes=False)
# @auth_params({})
# async def handler(request, **kwargs):
#     status = await request.app.rds.redis_db.get("fb_status")
#     if not status:
#         status = 0
#
#     motor_db = motor_base.get_db()
#
#     a = await motor_db.MiAstro.find_one()
#     logger.info("a %s" % a)
#     return json_encoder({"code": 0, "msg": "success", "data": {"status": int(status)}})
