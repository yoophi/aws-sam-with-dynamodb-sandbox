#!/bin/bash

aws dynamodb create-table --cli-input-json file://json/create-table.json --endpoint-url http://localhost:8000
