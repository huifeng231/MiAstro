#!/usr/bin/env python
from optparse import OptionParser

from aclients import AIOHttpClient
from sanic import Sanic
from sanic_scheduler import SanicScheduler

from database.mongodb import MotorBase
from database.redis import redis_handle
from database.redis.aio_redis import rds
from views import user_bp
from config import *
from sanic.response import text

app = Sanic('Order', strict_slashes=False)
scheduler = SanicScheduler(app)
environ_data = os.environ
app.config.update(
    {
        "ACLIENTS_REDIS_HOST": environ_data.get("ACLIENTS_REDIS_HOST", "127.0.0.1"),
        "ACLIENTS_REDIS_PORT": int(environ_data.get("ACLIENTS_REDIS_PORT", "6379")),
        "ACLIENTS_REDIS_DBNAME": 0,
        "ACLIENTS_REDIS_PASSWD": environ_data.get("ACLIENTS_REDIS_PASSWD"),
        "ACLIENTS_REDIS_POOL_SIZE": int(environ_data.get("ACLIENTS_REDIS_POOL_SIZE", 50)),

        'ACLIENTS_MONGO_HOST': environ_data.get("ACLIENTS_MONGO_HOST", "127.0.0.1"),
        'ACLIENTS_MONGO_PASSWD': environ_data.get("ACLIENTS_MONGO_PASSWD"),
        'ACLIENTS_MONGO_USERNAME': environ_data.get("ACLIENTS_MONGO_USERNAME"),
        'ACLIENTS_MONGO_PORT': int(environ_data.get("ACLIENTS_MONGO_PORT", "27017")),
        'ACLIENTS_MONGO_DBNAME': environ_data.get("ACLIENTS_MONGO_DBNAME", "local"),
        'ACLIENTS_MONGO_POOL_SIZE': 50,
    }
)

# 初始化redis
rds.init_app(app)
app.rds = rds

# 初始化aiohttp
requests = AIOHttpClient()
requests.init_app(app)
app.aio_req = requests

# 注册蓝图
app.blueprint(user_bp)


@app.listener('before_server_start')
async def setup(app, loop):
    motor_db = MotorBase().get_db()
    app.motor_db = motor_db
    app.conn = await redis_handle.create_connection_pool()


@app.middleware('response')
async def custom_banner(request, response):
    response.headers["Content-Type"] = "application/json; charset=UTF-8"
    response.headers["Access-Control-Allow-Origin"] = "*"


def main():
    parser = OptionParser(usage="usage: python %prog [options] filename",
                          version="order server v%s" % "1.0")
    parser.add_option("-p", "--port",
                      action="store",
                      type="int",
                      dest="port",
                      default=8686,
                      help="Listen Port")
    parser.add_option("-f", "--logfile",
                      action="store",
                      type="string",
                      dest="logfile",
                      default='./log/run.log',
                      help="LogFile Path and Name. default=./run.log")

    parser.add_option("-n", "--backupCount",
                      action="store",
                      type="int",
                      dest="backupCount",
                      default=10,
                      help="LogFile BackUp Number")
    parser.add_option("-m", "--master",
                      action="store_true",
                      dest="master",
                      default=False,
                      help="master process")
    parser.add_option("-d", "--debug",
                      action="store",
                      dest="debug",
                      type="int",
                      default=1,
                      help="debug mode")
    (options, args) = parser.parse_args()

    app.run(host='0.0.0.0', port=options.port, debug=True, access_log=True, workers=4, auto_reload=False)


@app.route("/")
async def test(request):
    return text('Hello world!')


if __name__ == '__main__':
    main()
    app.run(host="0.0.0.0", workers=1, port=8001, debug=False)
