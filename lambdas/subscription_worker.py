import logging

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sns = boto3.client('sns')
sfn = boto3.client('stepfunctions')


def lambda_handler(event, _):
    topic_arn = event['topicArn']

    while True:
        response = sns.list_subscriptions_by_topic(TopicArn=topic_arn)
        is_confirmed = response['Subscriptions'][0]['SubscriptionArn'] != 'PendingConfirmation'
        if is_confirmed:
            send_task_success(event)
            break


def send_task_success(event):
    logger.info(f'Calling SendTaskSuccess for activity: {event["activityArn"]}')
    sfn.send_task_success(
        taskToken=event['taskToken'],
        output='true'
    )


if __name__ == '__main__':
    input_task_token = 'paste_token_here'
    input_topic_arn = 'paste_topic_arn_here'
    input_activity_arn = 'paste_activity_arn_here'
    workflow_event = {
        'taskToken': input_task_token,
        'topicArn': input_topic_arn,
        'activityArn': input_activity_arn,
    }
    lambda_handler(workflow_event, None)
