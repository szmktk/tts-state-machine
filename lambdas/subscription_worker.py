import boto3

sns = boto3.client('sns')
sfn = boto3.client('stepfunctions')

def lambda_handler(event, context):
    topic_arn = event['topicArn']
    task_token = event['taskToken']
    activity_arn = event['activityArn']

    while True:
        response = sns.list_subscriptions_by_topic(TopicArn=topic_arn)
        is_confirmed = response['Subscriptions'][0]['SubscriptionArn'] != 'PendingConfirmation'
        if is_confirmed:
            print('Sending task success to activity: {}'.format(activity_arn))
            sfn.send_task_success(
                taskToken=task_token,
                output=str(is_confirmed).lower()
            )
            break


if __name__ == '__main__':
    ttoken = 'paste_token_here'
    topic_arn = 'paste_topic_arn_here'
    activity_arn = 'paste_activity_arn_here'
    event = {
        'taskToken': ttoken,
        'topicArn': topic_arn,
        'activityArn': activity_arn
    }
    lambda_handler(event, None)


