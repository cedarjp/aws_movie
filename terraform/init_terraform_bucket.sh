#!/usr/bin/env bash

set -ex

BUCKET_NAME=$1
PROFILE=$2
REGION=${3:-ap-northeast-1}

# バケットの作成
aws s3api create-bucket --bucket ${BUCKET_NAME} --profile ${PROFILE} --create-bucket-configuration LocationConstraint=${REGION}

# バケットのバージョニング設定
aws s3api put-bucket-versioning --bucket ${BUCKET_NAME} --profile ${PROFILE} --versioning-configuration Status=Enabled

# バケットのデフォルト暗号化設定
aws s3api put-bucket-encryption --bucket ${BUCKET_NAME} --profile ${PROFILE} --server-side-encryption-configuration '{
  "Rules": [
    {
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }
  ]
}'

aws s3api get-bucket-location --bucket ${BUCKET_NAME} --profile ${PROFILE}
aws s3api get-bucket-versioning --bucket ${BUCKET_NAME} --profile ${PROFILE}
aws s3api get-bucket-encryption --bucket ${BUCKET_NAME} --profile ${PROFILE}
