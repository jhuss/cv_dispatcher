#!/bin/env bash

# dependencies: python => 3.8, nodejs => 16

python3 -m venv .venv
source .venv/bin/activate
pip install wheel
pip install -r requeriments.txt

cd client/
npm install
