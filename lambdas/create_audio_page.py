import boto3
import os
import re

s3 = boto3.client('s3')

s3bucket = os.environ['STATIC_WEBSITE_BUCKET_NAME']


def lambda_handler(event, context):
    audio_url = event[0]['audioUrl']
    topic_arn = event[0]['topicArn']
    s3key = 'generated/{}.html'.format(re.search('\\d{5,}', audio_url).group(0))
    page_source = '<html> \
                    <div style="text-align: center"> \
                        <br/><br/><br/><br/><br/><br/><br/><br/>\
                        <img src="https://merapar.com/wp-content/uploads/2018/12/logo-donker.png" width=300><br/><br/><br/><br/> \
                    <body bgcolor="#F0F0F0"> \
                        <audio controls><source src="{}" type="audio/mp3"></audio> \
                    </body> \
                    </div> \
                </html>'.format(audio_url)

    s3.put_object(
        Body=page_source,
        Bucket=s3bucket,
        ContentType='text/html',
        Key=s3key
    )
    return {
        'topicArn': topic_arn,
        'siteUrl': get_site_url(s3key)
    }


def get_site_url(s3key):
    location = s3.get_bucket_location(Bucket=s3bucket)
    region = location['LocationConstraint']
    if region is None:
        url_begining = 'https://s3.amazonaws.com/'
    else:
        url_begining = 'https://s3-{}.amazonaws.com/'.format(str(region))
    return '{}{}/{}'.format(url_begining, s3bucket, s3key)


if __name__ == '__main__':
    event = {'audioUrl': 'https://s3-eu-west-1.amazonaws.com/tricity-ccg/audio/text_1548000855639086.mp3'}
    print(lambda_handler(event, None))
