#!/bin/bash

mkdir build
cd build
cp ../requirements.txt ../script_bovesp.py .

pip install -r requirements.txt -t .
zip -r lambda_function.zip .
mv lambda_function.zip ..
cd ..

rm -r build

