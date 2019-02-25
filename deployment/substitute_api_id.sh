#!/bin/bash

TARGET_STRING=new_api_id
TARGET_FILE=../ui/index.html

sed -E -i "" "s#https://(.*).execute-api.eu-west-1.amazonaws.com/demo#https://$TARGET_STRING.execute-api.eu-west-1.amazonaws.com/demo#" $TARGET_FILE
