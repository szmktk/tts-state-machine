# Activity Queue Polling module

## Purpose

This module is responsible for polling the state machine's activity queue.  
When the state machine enters the step which is an activity, it waits for an external worker to complete its operation and return the result of that operation using SendTaskSuccess API call.  
The purpose of this module is limited to polling the state machine indefinitely, and when the machine reaches the activity state this module will obtain a task token as a result of the polling operation.  
This token will be immediately dispatched to an external worker (`subscription-worker` lambda function) which will perform its logic and finally dispatch SendTaskSuccess API call.

## Deployment options

### Docker container
The recommended way is to run this script inside a Docker container on AWS, because that makes IAM authentication easier. The container needs to be run on an EC2 instance with the right IAM role, for example:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "states:GetActivityTask",
            "Resource": "arn:aws:states:${AWS::Region}:${AWS::AccountId}:activity:ProcessUsersSubscriptionActivity"
        },
        {
            "Effect": "Allow",
            "Action": "lambda:InvokeFunction",
            "Resource": "arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:subscription-worker"
        }
    ]
}
```

The following configuration parameters must be passed as environment variables:  
- `ACTIVITY_ARN` - the Amazon Resource Name of the activity being polled (defined in [docker-compose.yaml](docker-compose.yaml))  
- `AWS_REGION` - optionally if the region is not configured elsewhere  

Once the permissions and environment variables are in place run the following commands:

- build the Docker image:  
`docker build -t activity_queue_poller .` 

- run the image with docker-compose:
`docker-compose up -d`

- view the logs (container_id will be the output of the above `run` command):  
`docker logs -f $container_id`


### Standalone script

If one wants to just run the script, then just do not use Docker, but be sure to have the right permissions (like the role above) to run the code.  
Also, some environment variables are necessary:  
- `ACTIVITY_ARN` - the Amazon Resource Name of the activity being polled  
- `AWS_REGION` - optionally if the region is not configured elsewhere  

Usage examples:
- `python3 activity_queue_poller.py`  
or
- `chmod 744 activity_queue_poller.py && ./activity_queue_poller.py`
