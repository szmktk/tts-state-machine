import boto3

sns = boto3.client('sns')


def lambda_handler(event, _):
    sns.publish(
        TopicArn=event['topicArn'],
        Message=event['siteUrl']
    )
