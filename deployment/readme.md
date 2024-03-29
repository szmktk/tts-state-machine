# Deployment guide

This directory contains files necessary for the deployment process, namely the shell script that runs AWS CloudFormation CLI commands and the template itself.  

## Prerequisites:

- [AWS Credentials Setup](https://docs.aws.amazon.com/sdk-for-java/v1/developer-guide/setup-credentials.html)
- [Python](https://www.python.org/)
- [Boto 3 - The AWS SDK for Python](https://github.com/boto/boto3) (easily installable with `pip install boto3`)

## Usage:

First make sure you have AWS programmatic access credentials configured.  

Then make sure to provide two necessary bucket names in the config file:  
Note: [bucket names have to be globally unique](https://docs.aws.amazon.com/AmazonS3/latest/dev/BucketRestrictions.html) and have to be located in the same region as the rest of resources.  
`$EDITOR ${project_root}/deployment/config.ini`

Finally, just invoke the script:  
`./deploy.py`

Example output:
```
> ./deploy.py
INFO:botocore.credentials:Found credentials in shared credentials file: ~/.aws/credentials
INFO:root:Sending the lambda function package "/Users/ogre/workspace/tts-state-machine/deployment/archives/lambda-archive-1552346468.zip" to s3 bucket: "tccg-eurveuvr"
INFO:root:Upload successful
INFO:root:Creating CloudFormation stack...
INFO:root:Waiting for stack TextToSpeechDemo to be created
INFO:root:Stack TextToSpeechDemo created successfully
INFO:root:Fixing ApiGateway id in index.html file
INFO:root:Uploading files to static website bucket "tccg-eurveuvr-static":
INFO:root:Uploading ../ui/index.html
INFO:root:Uploading ../ui/logo-donker.png
INFO:root:Uploading ../ui/index.css
INFO:root:Uploading ../ui/background-main.jpg
INFO:root:The app's UI is accessible at: http://tccg-eurveuvr-static.s3-website-eu-west-1.amazonaws.com
```

Note the URL of the static website printed as the last line of the successful execution of the deployment script.

## Next step:  
For the app to run correctly the [Activity Queue Polling module](../utils/activity_queue_poller/readme.md) must be running.
