#!/bin/bash

# provide the name for artifacts (lambda packages, audio & text files) bucket:
BUCKET_NAME=
# provide the name for static website bucket:
STATIC_WEBSITE_BUCKET_NAME=

ACTION="$1"
ARCHIVE_DIR=$PWD/archives
ARCHIVE_NAME=lambda-archive-$(date +'%s').zip
STACK_NAME=TricityCCStack
TEMPLATE_FILE=resources.yaml
REGION=eu-west-1

if [[ "$BUCKET_NAME" == "" || "$STATIC_WEBSITE_BUCKET_NAME" == "" ]]
then
  echo "ERROR: please provide necessary configuration parameters inside the script"
  exit 1
fi

if [[ "$ACTION" != "create" && "$ACTION" != "update" && "$ACTION" != "c" && "$ACTION" != "u" ]]
then
  echo "usage: deploy.sh action"
  echo "deploy.sh: error: the following argument is required: action [ create | update | c | u ]"
  exit 1
fi

mkdir -p $ARCHIVE_DIR
cd ../lambdas
zip -r $ARCHIVE_DIR/$ARCHIVE_NAME *
echo "Deployment package created"
cd - 1>/dev/null

aws s3 cp $ARCHIVE_DIR/$ARCHIVE_NAME s3://$BUCKET_NAME/
echo "Deployment package sent to S3 bucket: $BUCKET_NAME"

if [[ "$ACTION" == "create" || "$ACTION" == "c" ]]
then
  echo "Creating CloudFormation stack..."
  aws cloudformation create-stack --stack-name $STACK_NAME --template-body file://$TEMPLATE_FILE --parameters ParameterKey=LambdaArchive,ParameterValue=$ARCHIVE_NAME ParameterKey=BucketName,ParameterValue=$BUCKET_NAME ParameterKey=StaticWebsiteBucketName,ParameterValue=$STATIC_WEBSITE_BUCKET_NAME --capabilities CAPABILITY_IAM --region $REGION
elif [[ "$ACTION" == "update" || "$ACTION" == "u" ]]
then
  echo "Updating CloudFormation stack..."
  aws cloudformation update-stack --stack-name $STACK_NAME --template-body file://$TEMPLATE_FILE --parameters ParameterKey=LambdaArchive,ParameterValue=$ARCHIVE_NAME ParameterKey=BucketName,ParameterValue=$BUCKET_NAME ParameterKey=StaticWebsiteBucketName,ParameterValue=$STATIC_WEBSITE_BUCKET_NAME --capabilities CAPABILITY_IAM --region $REGION
fi

echo "Sleeping for 120 seconds to let the stack deployment process complete..."
sleep 120

echo "Updating the ApiGateway id in index.html page..."
python3 substitute_api_id.py

echo "Uploading index.html page..."
aws s3 cp ../ui/ s3://$STATIC_WEBSITE_BUCKET_NAME/ --recursive

echo "Generating QR code..."
qrencode -s 20 -o index.png https://s3-$REGION.amazonaws.com/$STATIC_WEBSITE_BUCKET_NAME/index.html
