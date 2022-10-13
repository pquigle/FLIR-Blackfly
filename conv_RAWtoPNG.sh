#!/bin/bash

## Sanitization of inputs

if [ $# != 2 ]; then
  echo "USAGE: ./conv_RAWtoPNG.sh targetDirectory outputDirectory"
  exit 1

elif [[ ! -d $1 ]]; then
  echo "ERROR: Target directory does not exist"
  exit 1
fi


## Create output directory if it does not already exist

if [[ -d $2 ]]; then
  echo "Removing past directory..."
  rm -rI $2
fi

mkdir $2


## Recursively convert RAW files to PNG files

for RAW_Name in ${1}/*; do
  # Check that file is a RAW file
  if [ ${RAW_Name: -4} == ".raw" ]; then
    # Make new PNG name from RAW basename
    BASE="${RAW_Name##*/}"
    BASE="${BASE%.raw}"
    PNG_Name="${BASE}.png"

    # Convert RAW image format
    python3 raw_img_reader.py "${RAW_Name}" "${2}${PNG_Name}"
  fi
done
