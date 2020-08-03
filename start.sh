#!/bin/sh
echo "kill_server"
ps aux | grep 'sanic_server' | grep -v grep | awk '{print $2}'| xargs kill -9
#
#echo "start_server"
#nohup python sanic_server.py -p 8687 -d 1 >/dev/null &

APP_HOME=$(cd $(dirname $(dirname $0)); pwd)

echo "start server" $APP_HOME

export PYTHONPATH=$APP_HOME:$PYTHONPATH
nohup honcho -e env/dev.env run gunicorn -c config/gunicorn.py -k sanic.worker.GunicornWorker --access-logfile=log/access.log --error-logfile=log/error.log \
sanic_server:app >/dev/null &
# python -m process.do_task &

