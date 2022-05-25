#!/bin/sh

sh ./wait-for db:3306

sh ./wait-for rabbit:5672

sh ./wait-for redis:6379

exec "$@"