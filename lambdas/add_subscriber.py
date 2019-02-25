import boto3
import os
import re

sns = boto3.client('sns')

def lambda_handler(event, context):
    email = event['email']
    topic_arn = event['topicArn']
    if not is_user_subscribed(topic_arn):
        subscribe_user(topic_arn, email)


def is_user_subscribed(topic_arn):
    response = sns.list_subscriptions_by_topic(TopicArn=topic_arn)
    return len(response['Subscriptions']) is 1


def subscribe_user(topic_arn, email):
    return sns.subscribe(
        TopicArn=topic_arn,
        Protocol='email',
        Endpoint=email,
    )


if __name__ == '__main__':
    event = {
        'email': 'dev@example.com',
        'topicArn': 'arn:aws:sns:eu-west-1:880123456789:dev-example-com'
    }
    lambda_handler(event, None)
