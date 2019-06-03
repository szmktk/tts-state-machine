#!/usr/bin/env python3

import os
import re
import sys
import time
import boto3
import shutil
import mimetypes
import configparser
from argparse import ArgumentParser
from botocore.exceptions import ClientError


s3 = boto3.client('s3')
cf = boto3.client('cloudformation')
cf_resource = boto3.resource('cloudformation')
stack_name = 'TextToSpeechDemo'


def main(template):
    archive_path = create_archive()
    deploy_lambda_code(archive_path)
    deploy_stack(template, archive_path)
    deploy_ui_layer(static_website_bucket_name)


def create_archive():
    archive_dir = 'archives'
    archive_name = 'lambda-archive-{}'.format(round(time.time()))
    if not os.path.isdir(archive_dir):
        os.mkdir(archive_dir)
    return shutil.make_archive(os.path.join(archive_dir, archive_name), 'zip', '../lambdas')


def deploy_lambda_code(code_archive_path):
    create_deployment_bucket()
    if os.path.isfile(code_archive_path):
        print('INFO: Sending the lambda function package "{}" to s3 bucket: "{}"'.format(code_archive_path, artifacts_bucket_name))
        s3.upload_file(code_archive_path, artifacts_bucket_name, os.path.split(code_archive_path)[1])
        print('INFO: Upload successful.')
    else:
        print('ERROR: File not found: {}'.format(code_archive_path))
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
    deploy_wait = 30
    template_body = read_template_body(template)
    parameters = get_parameters(archive_path)
    try:
        create_stack(parameters, template_body)
    except ClientError as e:
        if not e.response['Error']['Code'] == 'AlreadyExistsException':
            raise
        else:
            print('INFO: Stack already exists, updating...')
            deploy_wait = update_stack(parameters, template_body)
    wait_until_deployed(deploy_wait)


def wait_until_deployed(wait_period):
    stack_status = None
    while stack_status not in ['CREATE_COMPLETE', 'UPDATE_COMPLETE']:
        if stack_status in ['ROLLBACK_IN_PROGRESS', 'ROLLBACK_COMPLETE', 'UPDATE_ROLLBACK_IN_PROGRESS', 'UPDATE_ROLLBACK_COMPLETE']:
            print('ERROR: Stack deployment failed!')
            sys.exit(1)
        print('INFO: Checking if stack deployment is complete in {} seconds...'.format(wait_period))
        stack_status = cf_resource.Stack(stack_name).stack_status
        time.sleep(wait_period)
    print('INFO: Stack deployment complete!')


def create_stack(parameters, template):
    print('INFO: Creating CloudFormation stack...')
    cf.create_stack(
        StackName=stack_name,
        TemplateBody=template,
        Parameters=parameters,
        Capabilities=['CAPABILITY_IAM']
    )


def update_stack(parameters, template):
    try:
        cf.update_stack(
            StackName=stack_name,
            TemplateBody=template,
            Parameters=parameters,
            Capabilities=['CAPABILITY_IAM']
        )
        return 5
    except ClientError as e:
        if e.response['Error']['Message'] == 'No updates are to be performed.':
            print('INFO: No CloudFormation stack updates are to be performed')
            return 0


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
    print('INFO: Uploading files to static website bucket "{}":'.format(bucket_name))
    for name in os.listdir(ui_path):
        localpath = os.path.join(ui_path, name)
        if os.path.isfile(localpath):
            print('INFO: Uploading {}'.format(localpath))
            upload_file_with_metadata(localpath, bucket_name, name)
    print_website_url()


def upload_file_with_metadata(localpath, bucket_name, name):
    mimetype = mimetypes.guess_type(localpath)[0]
    s3.upload_file(localpath, bucket_name, name, ExtraArgs={'ContentType': mimetype})


def substitute_api_id():
    apis = boto3.client('apigateway').get_rest_apis()
    for api in apis['items']:
        if api['name'] == 'TricityCloudComputingApi':
            print('INFO: Fixing ApiGateway id in index.html file')
            with open('../ui/index.html', 'r') as f:
                lines = f.readlines()
            with open('../ui/index.html', 'w') as f:
                for line in lines:
                    f.write(re.sub(r'https://[a-z0-9]{10}.execute-api', 'https://{}.execute-api'.format(api['id']), line))
            return
    print('WARN: No api with name "TricityCloudComputingApi" found! Please fix ApiGateway id manually.')


def print_website_url():
    stack_outputs = cf_resource.Stack(stack_name).outputs
    website_url = stack_outputs[0]['OutputValue']
    print('INFO: The app\'s UI is accessible at: {}'. format(website_url))


def validate_bucket_names(b1, b2):
    pattern = re.compile('(?=^.{3,63}$)(?!^(\\d+\\.)+\\d+$)(^(([a-z0-9]|[a-z0-9][a-z0-9\\-]*[a-z0-9])\\.)*([a-z0-9]|[a-z0-9][a-z0-9\\-]*[a-z0-9])$)')
    if not pattern.match(b1) or not pattern.match(b2):
        print('ERROR: Missing or faulty configuration variables. Please provide valid bucket names in the config.ini file')
        sys.exit(1)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-t', '--template', metavar='template', default='resources.yaml', help='The path to the CloudFormation template (default="resources.yaml").')
    parser.add_argument('-c', '--config', metavar='configfile', default='config.ini', help='The path to the app configuration file (default="config.ini").')
    args = parser.parse_args()

    if not os.path.isfile(args.template) or not os.path.isfile(args.config):
        print('ERROR: "resources.yaml" or "config.ini" file is missing, please provide them both or specify a path using "-t" and "-c" options.')
        sys.exit(1)

    config = configparser.ConfigParser()
    config.read(args.config)
    static_website_bucket_name = config['default']['static_website_bucket_name']
    artifacts_bucket_name = config['default']['artifacts_bucket_name']
    validate_bucket_names(static_website_bucket_name, artifacts_bucket_name)

    sys.exit(main(args.template))
