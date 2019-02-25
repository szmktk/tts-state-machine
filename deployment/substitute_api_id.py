import boto3
import os
import re

session = boto3.session.Session()
region = os.environ.get('AWS_REGION', session.region_name)
api_gw = boto3.client('apigateway', region_name=region)


def main():
    response = api_gw.get_rest_apis()

    for api in response['items']:
        if api['name'] == 'TricityCloudComputingApi':
            substitute_in_index(api['id'])


def substitute_in_index(rest_api_id):
    with open('../ui/index.html', 'r') as f:
        lines = f.readlines()
    with open('../ui/index.html', 'w') as f:
        for line in lines:
            f.write(re.sub(r'https://[a-z0-9]{10}.execute-api', 'https://{}.execute-api'.format(rest_api_id), line))


if __name__ == '__main__':
    main()
