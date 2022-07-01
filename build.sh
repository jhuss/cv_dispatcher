#!/bin/env bash

export APP_MODE="prod"

cd client/
npm install
npm run build
