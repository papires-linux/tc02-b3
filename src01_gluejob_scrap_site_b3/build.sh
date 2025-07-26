#!/bin/bash

mkdir build
cd build
cp ../requirements.txt ../script_bovesp_aws_glue.py .

pip3 install -r requirements.txt -t .
zip -r lambda_function.zip .
mv lambda_function.zip ..
cd ..

rm -r build

