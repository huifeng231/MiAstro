#!/bin/sh
echo "kill_server"
ps aux | grep 'sanic_server' | grep -v grep | awk '{print $2}'| xargs kill -9