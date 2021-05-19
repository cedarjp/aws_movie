#!/usr/bin/env bash

set -ex

TABLE_NAME=$1
PROFILE=$2

aws dynamodb create-table \
    --profile ${PROFILE} \
	--table-name ${TABLE_NAME} \
	--attribute-definitions AttributeName=LockID,AttributeType=S \
	--key-schema AttributeName=LockID,KeyType=HASH \
	--provisioned-throughput ReadCapacityUnits=1,WriteCapacityUnits=1
