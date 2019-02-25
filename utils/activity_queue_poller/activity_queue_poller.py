#!/usr/bin/env python3

import boto3
import json
import sys
import os
from datetime import datetime
from botocore.client import Config
from botocore.exceptions import ReadTimeoutError

session = boto3.session.Session()
region = os.environ.get('AWS_REGION', session.region_name)
print('Running in {} region.'.format(region))

# sfn = boto3.client('stepfunctions', region_name=region, config=Config(connect_timeout=65, read_timeout=65))
sfn = boto3.client('stepfunctions', region_name=region)
awslambda = boto3.client('lambda', region_name=region)


worker_name = 'subscription-worker'
activity_arn = os.environ['ACTIVITY_ARN']


def main():
    while True:
        try:
            print('Calling GetActivityTask at {}'.format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')))
            activity_task = sfn.get_activity_task(activityArn=activity_arn)
            print('Got response at {}'.format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')))
            if activity_task:
                task_token = activity_task.get('taskToken')
                if task_token is not None:
                    print('Activity task found: {}'.format(task_token))
                    activity_input = json.loads(activity_task['input'])
                    topic_arn = activity_input['topicArn']
                    lambda_input = {
                        'taskToken': task_token,
                        'topicArn': topic_arn,
                        'activityArn': activity_arn
                    }
                    invoke_worker(lambda_input)
                else:
                    print('WARN: Could not retrieve taskToken!')
        except ReadTimeoutError as e:
            print(e)


def invoke_worker(lambda_input):
    response = awslambda.invoke(
        FunctionName=worker_name,
        Payload=json.dumps(lambda_input)
    )
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        print('Function "{}" has been invoked successfully.'.format(worker_name))

if __name__ == '__main__':
    sys.exit(main())
