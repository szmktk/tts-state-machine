# Deployment guide

This directory contains files necessary for the deployment process, namely the shell script that runs AWS CloudFormation CLI commands and the template itself.  

## Usage:
First make sure you have AWS programmatic access credentials configured and AWS command line tools installed:  
- [AWS Credentials Setup](https://docs.aws.amazon.com/sdk-for-java/v1/developer-guide/setup-credentials.html)  
- [AWS CLI Installation](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html)  
- Optionally the [qrencode CLI tool](https://fukuchi.org/works/qrencode/) will be handy to generate the QR code with the website url (install it easily with Python's `pip`, MacOS's `brew` or via Linux package manager)

Then make sure to provide two necessary bucket names inside the script:  
Note: [bucket names have to be globally unique](https://docs.aws.amazon.com/AmazonS3/latest/dev/BucketRestrictions.html)  
`$EDITOR ${project_root}/deployment/deploy.sh`

Finally just invoke the script:  
`./deploy.sh create`

Example output:
```
> ./deploy.sh create
  adding: add_subscriber.py (deflated 53%)
  adding: convert_to_audio.py (deflated 63%)
  adding: create_audio_page.py (deflated 55%)
  adding: create_user_topic.py (deflated 32%)
  adding: save_text_to_s3.py (deflated 45%)
  adding: send_email.py (deflated 27%)
  adding: start_execution.py (deflated 50%)
  adding: subscription_worker.py (deflated 58%)
Deployment package created
upload: archives/lambda-archive-1550413028.zip to s3://tricity-ccg/lambda-archive-1550413028.zip
Deployment package sent to S3 bucket: tricity-ccg
Creating CloudFormation stack...
{
    "StackId": "arn:aws:cloudformation:eu-west-1:************:stack/TricityCCStack/f20cacc0-1ceb-11e9-8f1f-0233b49b0800"
}
Sleeping for 120 seconds to let the stack deployment process complete...
Updating the ApiGateway id in index.html page...
Uploading index.html page...
upload: ../ui/index.html to s3://tricity-ccg-static/index.html
upload: ../ui/index.css to s3://tricity-ccg-static/index.css
upload: ../ui/logo-donker.png to s3://tricity-ccg-static/logo-donker.png
upload: ../ui/background-main.jpg to s3://tricity-ccg-static/background-main.jpg
Generating QR code...
```

Now get the URL of the static website by viewing the outputs of the stack via the console or with the following command:  
`aws cloudformation describe-stacks`

## Next step:  
For the app to run correctly the [Activity Queue Polling module](../utils/activity_queue_poller/readme.md) must be running.

**NOTE:** For the subsequent runs of the deployment script (after the stack has been deployed successfully at least once) use the `update` option:  
`./deploy.sh update`
