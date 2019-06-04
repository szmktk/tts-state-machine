import boto3

sns = boto3.client('sns')

def lambda_handler(event, context):
    sns.publish(
        TopicArn=event['topicArn'],
        Message=event['siteUrl']
    )
