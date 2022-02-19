import boto3
import re

sns = boto3.client('sns')


def lambda_handler(event, _):
    email = event['email']
    topic_name = re.sub('[@.]', '-', email)
    response = sns.create_topic(Name=topic_name)
    return response['TopicArn']
