# Deployment guide

This directory contains files necessary for the deployment process, namely the shell script that runs AWS CloudFormation CLI commands and the template itself.  

## Prerequisites:
- [AWS Credentials Setup](https://docs.aws.amazon.com/sdk-for-java/v1/developer-guide/setup-credentials.html)
- [Python](https://www.python.org/)
- [Boto 3 - The AWS SDK for Python](https://github.com/boto/boto3) (easily installable with `pip install boto3`)

## Usage:
First make sure you have AWS programmatic access credentials configured.  

Then make sure to provide two necessary bucket names in the config file:  
Note: [bucket names have to be globally unique](https://docs.aws.amazon.com/AmazonS3/latest/dev/BucketRestrictions.html)  
`$EDITOR ${project_root}/deployment/config.ini`

Finally just invoke the script:  
`./deploy.py`

Example output:
```
> ./deploy.py
INFO: Sending the lambda function package "/Users/ogre/workspace/tts-state-machine/deployment/archives/lambda-archive-1552346468.zip" to s3 bucket: "tccg-eurveuvr"
INFO: Upload successful.
INFO: Creating CloudFormation stack..
INFO: Checking if stack deployment is complete in 30 seconds...
INFO: Checking if stack deployment is complete in 30 seconds...
INFO: Checking if stack deployment is complete in 30 seconds...
INFO: Checking if stack deployment is complete in 30 seconds...
INFO: Stack deployment complete!
INFO: Fixing ApiGateway id in index.html file
INFO: Uploading files to static website bucket "tccg-eurveuvr-static":
INFO: Uploading ../ui/index.html
INFO: Uploading ../ui/logo-donker.png
INFO: Uploading ../ui/index.css
INFO: Uploading ../ui/background-main.jpg
INFO: The app's UI is accessible at: http://tccg-eurveuvr-static.s3-website-eu-west-1.amazonaws.com
```

Note the URL of the static website printed as the last line of the successful execution of the deployment script.

## Next step:  
For the app to run correctly the [Activity Queue Polling module](../utils/activity_queue_poller/readme.md) must be running.
