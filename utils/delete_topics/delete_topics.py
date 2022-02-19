import boto3
import os

session = boto3.session.Session()
region = os.environ.get('AWS_REGION', session.region_name)
sns = boto3.client('sns', region_name=region)


def main():
    response = sns.list_topics()
    topics = response['Topics']
    for topic in topics:
        sns.delete_topic(TopicArn=topic['TopicArn'])


if __name__ == '__main__':
    main()
