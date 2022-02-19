import boto3
import os
from contextlib import closing

s3 = boto3.client('s3')
voice = os.environ.get('VOICE', 'Joanna')


def lambda_handler(event, _):
    bucket = event['savedText']['bucket']
    key = event['savedText']['key']
    file_name = key[5:]

    save_text_file_locally(bucket, key, file_name)
    content = read_text_file(file_name)
    audio_stream = convert_text_to_speech(content)
    save_audio_file_locally(audio_stream, file_name)
    new_key = save_audio_file_to_s3(bucket, file_name)
    return get_site_url(bucket, new_key)


def save_text_file_locally(bucket, key, file_name):
    s3.download_file(bucket, key, f'/tmp/{file_name}')


def read_text_file(file_name):
    with open(f'/tmp/{file_name}', 'r') as f:
        return f.read().replace('\n', '')


def convert_text_to_speech(content):
    polly = boto3.client('polly')
    return polly.synthesize_speech(
        OutputFormat='mp3',
        Text=content,
        TextType='text',
        VoiceId=voice
    )


def save_audio_file_locally(audio_stream, file_name):
    if 'AudioStream' in audio_stream:
        with closing(audio_stream['AudioStream']) as stream:
            handle_audio_stream(stream, file_name)


def handle_audio_stream(stream, file_name):
    output = os.path.join('/tmp/', file_name)
    with open(output, 'wb') as file:
        file.write(stream.read())


def save_audio_file_to_s3(bucket, file_name):
    new_key = 'audio/' + file_name + '.mp3'
    s3.upload_file('/tmp/' + file_name, bucket, new_key)
    s3.put_object_acl(ACL='public-read', Bucket=bucket, Key=new_key)
    return new_key


def get_site_url(bucket, new_key):
    location = s3.get_bucket_location(Bucket=bucket)
    region = location['LocationConstraint']
    if region is None:
        url_beginning = 'https://s3.amazonaws.com/'
    else:
        url_beginning = f'https://s3-{str(region)}.amazonaws.com/'
    return f'{url_beginning}{bucket}/{new_key}'
