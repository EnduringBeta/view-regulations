#!/bin/bash

if [ -z "$1" ]; then
  echo "Database password required"
  exit 1
fi

MYSQL_PASSWORD="$1"

mysql -u root -p$MYSQL_PASSWORD < clear.sql
