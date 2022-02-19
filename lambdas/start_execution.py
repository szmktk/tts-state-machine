import json
import logging
import os
import random

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sfn = boto3.client('stepfunctions')

STATE_MACHINE_ARN = os.environ['STATE_MACHINE_ARN']


def lambda_handler(event, _):
    user_input = event['body'].split('\r\n')
    text = user_input[0][2:]
    email = user_input[1][2:]
    execution_name = f'{email}-{f"{random.randrange(10 ** 8):08}"}'
    logger.info(f'Starting execution of state machine: {STATE_MACHINE_ARN}')
    sfn.start_execution(
        stateMachineArn=STATE_MACHINE_ARN,
        name=execution_name,
        input=json.dumps({'text': text, 'email': email, 'execution_name': execution_name})
    )

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/html; charset=utf-8',
        },
        'body': prepare_response()
    }


def prepare_response():
    return '<html> \
                <div style="text-align: center"> \
                    <br/><br/><br/><br/><br/><br/><br/><br/>\
                    <h2>Please check your mailbox</h2><br/> \
                    <h2>In order to continue, please click on the "Confirm subscription" link in the email you\'ve received</h2><br/> \
                <body bgcolor="#F0F0F0"> \
                </body> \
                </div> \
            </html>'


if __name__ == '__main__':
    ui_event = {'body': 'this text will get converted'}
    lambda_handler(ui_event, None)
