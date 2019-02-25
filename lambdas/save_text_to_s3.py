import os
import boto3


def lambda_handler(event, context):
    s3 = boto3.client('s3')
    bucket = os.environ['BUCKET_NAME']
    key = 'text/text_{}'.format(event['execution_name'])
    text = event['text']

    response = s3.put_object(
        Body=text,
        Bucket=bucket,
        ContentType='text/plain; charset=utf-8',
        Key=key,
    )
    return {
        'bucket': bucket,
        'key': key,
        'body': 'Successfully uploaded file: {} to bucket: {}'.format(key, bucket)
    }

if __name__ == '__main__':
    event = {
        'text': 'x=this is text that will be saved to s3',
        'email': 'dev@example.com',
        'execution_name': 'dev@example.com-57224180'
    }
    print(lambda_handler(event, None))
