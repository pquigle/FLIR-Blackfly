#!/bin/bash

if [ $# != 2 ]; then
  echo "Usage: bash getJSON.sh YYMMDD hhmmss"
  exit 0
fi

if [ ! -d data/$1/ECSV/ ]; then
  mkdir -v data/$1/ECSV/
  mkdir -v data/$1/ECSV/$2/
elif [ ! -d data/$1/ECSV/$2/ ]; then
  mkdir -v data/$1/ECSV/$2/
fi

find data/$1 -wholename *$2*/*.ecsv -exec cp -v {} data/$1/ECSV/$2/ \;
