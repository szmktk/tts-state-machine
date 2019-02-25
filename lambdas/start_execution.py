import boto3
import os
import json
import random

sfn = boto3.client('stepfunctions')

def lambda_handler(event, context):
    user_input = event['body'].split('\r\n')
    text = user_input[0][2:]
    email = user_input[1][2:]
    execution_name = '{}-{}'.format(email, '{:08}'.format(random.randrange(10**8)))
    response = sfn.start_execution(
        stateMachineArn=os.environ['STATE_MACHINE_ARN'],
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
                    <h2>Sprawdź swoją skrzynkę pocztową</h2><br/> \
                    <h2>W ciągu pięciu minut potwierdź subskrypcję tematu SNS by przejść dalej</h2><br/> \
                <body bgcolor="#F0F0F0"> \
                </body> \
                </div> \
            </html>'


if __name__ == '__main__':
    event = {'body': 'this text will get converted'}
    lambda_handler(event, None)
