# coding=utf-8

import boto3

PREDICTION_INSTANCE_ID = "${instance_id}"
COMMAND = '/home/ec2-user/aws_movie/predict.py {} {}'

s3 = boto3.client('s3')
ssm = boto3.client('ssm')
transcoder = boto3.client('elastictranscoder', 'ap-northeast-1')


def lambda_handler(event, context):
    for d in event['Records']:
        bucket_name = d['s3']['bucket']['name']
        input_key = d['s3']['object']['key']
        command = COMMAND.format(
            bucket_name,
            input_key
        )
        result = ssm.send_command(
            InstanceIds=[PREDICTION_INSTANCE_ID],
            DocumentName="AWS-RunShellScript",
            Parameters={
                "commands": [
                    command
                ],
                "executionTimeout": ["18000"]
            },
        )
    return True
