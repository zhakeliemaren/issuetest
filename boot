#!/bin/bash

# usage:
# docker run -d --net=host -v /path/to/env.ini:/data/ob-robot/env.ini  obrobot:1.0.0 ./start.sh -s backend
# docker run -d --net=host -v /path/to/env.ini:/data/ob-robot/env.ini  obrobot:1.0.0 ./start.sh -s crontab

# init env
if [[ ! -f env.ini ]]; then
    echo "env.ini missing"
    exit 1
fi
source env.ini

usage()
{
  echo "Usage:"
  echo "  start.sh -s <service>"
  echo "Supported service: backend crontab "
  echo "Default service is: backend"
  exit 0
}

TEMP=`getopt -o s:h -- "$@"`
eval set -- "$TEMP"

while true ; do
  case "$1" in
    -h) usage; shift ;;
    -s) service=$2; shift 2 ;;
    --) shift; break;;
    *) echo "Usupported option"; exit 1;;
  esac
done

if [[ x"$service" == x"backend" ]]; then
    # 启动后端服务
    python3 main.py
else
    echo "Unsupported service"
    exit 1
fi