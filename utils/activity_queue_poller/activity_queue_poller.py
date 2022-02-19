#!/usr/bin/env python3

import json
import logging
import os
import sys
from datetime import datetime

import boto3
from botocore.exceptions import ReadTimeoutError

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

session = boto3.session.Session()
region = os.environ.get('AWS_REGION', session.region_name)
logger.info(f'Running in {region} region.')

sfn = boto3.client('stepfunctions', region_name=region)
awslambda = boto3.client('lambda', region_name=region)

worker_name = 'subscription-worker'
activity_arn = os.environ['ACTIVITY_ARN']


def main():
    while True:
        try:
            poll()
        except ReadTimeoutError as e:
            logger.error(f'Timeout error while calling AWS StepFunctions API: {str(e)}')


def poll():
    logger.info(f'Calling GetActivityTask at {datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")}')
    activity_task = sfn.get_activity_task(activityArn=activity_arn)
    logger.info(f'Got response at {datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")}')
    if activity_task:
        task_token = activity_task.get('taskToken')
        if task_token is not None:
            logger.info(f'Activity task found: {task_token}')
            activity_input = json.loads(activity_task['input'])
            topic_arn = activity_input['topicArn']
            lambda_input = {
                'taskToken': task_token,
                'topicArn': topic_arn,
                'activityArn': activity_arn
            }
            invoke_worker(lambda_input)
        else:
            logger.warning('Could not retrieve taskToken!')


def invoke_worker(lambda_input):
    response = awslambda.invoke(
        FunctionName=worker_name,
        Payload=json.dumps(lambda_input)
    )
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        logger.info(f'Function "{worker_name}" has been invoked successfully.')


if __name__ == '__main__':
    sys.exit(main())
