import os
import re

import boto3

s3 = boto3.client('s3')

S3_BUCKET = os.environ['STATIC_WEBSITE_BUCKET_NAME']


def lambda_handler(event, _):
    audio_url = event[0]['audioUrl']
    topic_arn = event[0]['topicArn']
    audio_id = re.search('\\d{5,}', audio_url).group(0)
    s3_key = f'generated/{audio_id}.html'
    page_source = f'<html> \
                    <div style="text-align: center"> \
                        <br/><br/><br/><br/><br/><br/><br/><br/>\
                        <img src="https://merapar.com/app/themes/merapar/img/base/logo-white.png" width=300><br/><br/><br/><br/> \
                    <body bgcolor="#F0F0F0"> \
                        <audio controls><source src="{audio_url}" type="audio/mp3"></audio> \
                    </body> \
                    </div> \
                </html>'

    s3.put_object(
        Body=page_source,
        Bucket=S3_BUCKET,
        ContentType='text/html',
        Key=s3_key
    )
    return {
        'topicArn': topic_arn,
        'siteUrl': get_site_url(s3_key)
    }


def get_site_url(s3_key):
    location = s3.get_bucket_location(Bucket=S3_BUCKET)
    region = location['LocationConstraint']
    if region is None:
        url_beginning = 'https://s3.amazonaws.com/'
    else:
        url_beginning = f'https://s3-{str(region)}.amazonaws.com/'
    return f'{url_beginning}{S3_BUCKET}/{s3_key}'


if __name__ == '__main__':
    lambda_event = {'audioUrl': 'https://s3-eu-west-1.amazonaws.com/tricity-ccg/audio/text_1548000855639086.mp3'}
    print(lambda_handler(lambda_event, None))
