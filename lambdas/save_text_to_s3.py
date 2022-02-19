import os

import boto3


def lambda_handler(event, _):
    s3 = boto3.client('s3')
    bucket_name = os.environ['BUCKET_NAME']
    key = f'text/text_{event["execution_name"]}'
    text = event['text']

    s3.put_object(
        Body=text,
        Bucket=bucket_name,
        ContentType='text/plain; charset=utf-8',
        Key=key,
    )

    return {
        'bucket': bucket_name,
        'key': key,
        'body': f'Successfully uploaded file: {key} to bucket: {bucket_name}'
    }


if __name__ == '__main__':
    lambda_event = {
        'text': 'x=this is text that will be saved to s3',
        'email': 'dev@example.com',
        'execution_name': 'dev@example.com-57224180'
    }
    print(lambda_handler(lambda_event, None))
