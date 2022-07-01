#!/bin/env bash

export APP_MODE="prod"

./build.sh

source .venv/bin/activate
python run.py
