#!/usr/bin/env python3
import configparser
import logging
import mimetypes
import os
import re
import shutil
import sys
import time
from argparse import ArgumentParser

import boto3
from botocore.exceptions import ClientError

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client('s3')
cf = boto3.client('cloudformation')

INDEX_FILE_PATH = '../ui/index.html'
S3_BUCKET_NAME_VALIDATION_REGEX = '(?=^.{3,63}$)(?!^(\\d+\\.)+\\d+$)(^(([a-z0-9]|[a-z0-9][a-z0-9\\-]*[a-z0-9])\\.)*([a-z0-9]|[a-z0-9][a-z0-9\\-]*[a-z0-9])$)'
STACK_NAME = 'TextToSpeechDemo'


def main(template):
    archive_path = create_archive()
    deploy_lambda_code(archive_path)
    deploy_stack(template, archive_path)
    deploy_ui_layer(static_website_bucket_name)


def create_archive():
    archive_dir = 'archives'
    archive_name = f'lambda-archive-{round(time.time())}'
    if not os.path.isdir(archive_dir):
        os.mkdir(archive_dir)
    return shutil.make_archive(os.path.join(archive_dir, archive_name), 'zip', '../lambdas')


def deploy_lambda_code(code_archive_path):
    create_deployment_bucket()
    if os.path.isfile(code_archive_path):
        logger.info(f'Sending the lambda function package "{code_archive_path}" to s3 bucket: "{artifacts_bucket_name}"')
        s3.upload_file(code_archive_path, artifacts_bucket_name, os.path.split(code_archive_path)[1])
        logger.info('Upload successful')
    else:
        logger.error(f'File not found: {code_archive_path}')
        sys.exit(1)


def create_deployment_bucket():
    my_session = boto3.session.Session()
    my_region = my_session.region_name
    try:
        s3.create_bucket(
            Bucket=artifacts_bucket_name,
            CreateBucketConfiguration={'LocationConstraint': my_region}
        )
    except ClientError as e:
        if not e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
            raise


def deploy_stack(template, archive_path):
    template_body = read_template_body(template)
    parameters = get_parameters(archive_path)
    try:
        create_stack(parameters, template_body)
    except ClientError as e:
        if not e.response['Error']['Code'] == 'AlreadyExistsException':
            raise
        else:
            logger.info('Stack already exists, updating...')
            update_stack(parameters, template_body)


def create_stack(parameters, template):
    logger.info('Creating CloudFormation stack...')
    cf.create_stack(
        StackName=STACK_NAME,
        TemplateBody=template,
        Parameters=parameters,
        Capabilities=['CAPABILITY_IAM']
    )

    waiter = cf.get_waiter('stack_create_complete')
    logger.info(f'Waiting for stack {STACK_NAME} to be created')
    waiter.wait(StackName=STACK_NAME)
    logger.info(f'Stack {STACK_NAME} created successfully')


def update_stack(parameters, template):
    try:
        cf.update_stack(
            StackName=STACK_NAME,
            TemplateBody=template,
            Parameters=parameters,
            Capabilities=['CAPABILITY_IAM']
        )
    except ClientError as e:
        if e.response['Error']['Message'] == 'No updates are to be performed.':
            logger.info('No CloudFormation stack updates are to be performed')

    waiter = cf.get_waiter('stack_update_complete')
    logger.info(f'Waiting for stack {STACK_NAME} to be updated')
    waiter.wait(
        StackName=STACK_NAME,
        WaiterConfig={'Delay': 5}
    )
    logger.info(f'Stack {STACK_NAME} updated successfully')


def read_template_body(template):
    with open(template) as f:
        return f.read()


def get_parameters(archive_path):
    return [
        {
            'ParameterKey': 'LambdaArchive',
            'ParameterValue': os.path.basename(archive_path)
        },
        {
            'ParameterKey': 'ArtifactsBucketName',
            'ParameterValue': artifacts_bucket_name
        },
        {
            'ParameterKey': 'StaticWebsiteBucketName',
            'ParameterValue': static_website_bucket_name
        },
    ]


def deploy_ui_layer(bucket_name):
    substitute_api_id()
    ui_path = '../ui'
    logger.info(f'Uploading files to static website bucket "{bucket_name}":')
    for name in os.listdir(ui_path):
        local_path = os.path.join(ui_path, name)
        if os.path.isfile(local_path):
            logger.info(f'Uploading {local_path}')
            upload_file_with_metadata(local_path, bucket_name, name)
    print_website_url()


def upload_file_with_metadata(local_path, bucket_name, name):
    mimetype = mimetypes.guess_type(local_path)[0]
    s3.upload_file(local_path, bucket_name, name, ExtraArgs={'ContentType': mimetype})


def substitute_api_id():
    apis = boto3.client('apigateway').get_rest_apis()
    for api in apis['items']:
        if api['name'] == 'TricityCloudComputingApi':
            perform_substitution(api)
            return
    logger.warning('No api with name "TricityCloudComputingApi" found! Please fix ApiGateway id manually.')


def perform_substitution(api):
    logger.info('Fixing ApiGateway id in index.html file')
    with open(INDEX_FILE_PATH, 'r') as f:
        lines = f.readlines()
    with open(INDEX_FILE_PATH, 'w') as f:
        for line in lines:
            f.write(re.sub(r'https://[a-z0-9]{10}.execute-api', f'https://{api["id"]}.execute-api', line))


def print_website_url():
    response = cf.describe_stacks(StackName=STACK_NAME)
    website_url = response['Stacks'][0]['Outputs'][0]['OutputValue']
    logger.info(f'The app\'s UI is accessible at: {website_url}')


def validate_bucket_name(bucket_name):
    pattern = re.compile(S3_BUCKET_NAME_VALIDATION_REGEX)
    if not pattern.match(bucket_name):
        logger.error('Missing or faulty configuration variables. Please provide valid bucket names in the config.ini file')
        sys.exit(1)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-t', '--template', metavar='template', default='resources.yaml', help='The path to the CloudFormation template (default="resources.yaml").')
    parser.add_argument('-c', '--config', metavar='configfile', default='config.ini', help='The path to the app configuration file (default="config.ini").')
    args = parser.parse_args()

    if not os.path.isfile(args.template) or not os.path.isfile(args.config):
        logger.error('"resources.yaml" or "config.ini" file is missing, please provide them both or specify a path using "-t" and "-c" options.')
        sys.exit(1)

    config = configparser.ConfigParser()
    config.read(args.config)
    artifacts_bucket_name = config['default']['artifacts_bucket_name']
    validate_bucket_name(artifacts_bucket_name)
    static_website_bucket_name = config['default']['static_website_bucket_name']
    validate_bucket_name(static_website_bucket_name)

    sys.exit(main(args.template))
