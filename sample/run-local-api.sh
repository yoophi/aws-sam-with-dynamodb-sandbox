#!/bin/bash

sam build
sam local start-api --env-vars ./json/local-env.json --port 3000
