#!/bin/bash
awslocal s3 mb s3://source-images/
awslocal s3 mb s3://zip-storage/

awslocal s3 cp /tmp/source.jpg s3://source-images/source.jpg

DLQ_SQS=input-queue-dlq
SOURCE_SQS=input-queue

QUEUE_URL=$(awslocal sqs --region eu-west-1 create-queue --queue-name $DLQ_SQS | grep '"QueueUrl"' | awk -F '"QueueUrl":' '{print $2}' | tr -d '"' | xargs)

DLQ_SQS_ARN=$(awslocal sqs --region eu-west-1 get-queue-attributes \
                  --attribute-name QueueArn --queue-url=$QUEUE_URL \
                  |  sed 's/"QueueArn"/\n"QueueArn"/g' | grep '"QueueArn"' | awk -F '"QueueArn":' '{print $2}' | tr -d '"' | xargs)

awslocal sqs --region eu-west-1 create-queue --queue-name $SOURCE_SQS \
     --attributes '{
                   "RedrivePolicy": "{\"deadLetterTargetArn\":\"'"$DLQ_SQS_ARN"'\",\"maxReceiveCount\":\"2\"}",
                   "VisibilityTimeout": "20"
                   }'


DLQ_SQS=output-queue-dlq
SOURCE_SQS=output-queue

QUEUE_URL=$(awslocal sqs --region eu-west-1 create-queue --queue-name $DLQ_SQS | grep '"QueueUrl"' | awk -F '"QueueUrl":' '{print $2}' | tr -d '"' | xargs)

DLQ_SQS_ARN=$(awslocal sqs --region eu-west-1 get-queue-attributes \
                  --attribute-name QueueArn --queue-url=$QUEUE_URL \
                  |  sed 's/"QueueArn"/\n"QueueArn"/g' | grep '"QueueArn"' | awk -F '"QueueArn":' '{print $2}' | tr -d '"' | xargs)

awslocal sqs --region eu-west-1 create-queue --queue-name $SOURCE_SQS \
     --attributes '{
                   "RedrivePolicy": "{\"deadLetterTargetArn\":\"'"$DLQ_SQS_ARN"'\",\"maxReceiveCount\":\"2\"}",
                   "VisibilityTimeout": "20"
                   }'
