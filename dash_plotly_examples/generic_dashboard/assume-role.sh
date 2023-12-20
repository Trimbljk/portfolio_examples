#!/usr/bin/env bash

unset AWS_ACCESS_KEY_ID
unset AWS_SECRET_ACCESS_KEY
unset AWS_SESSION_TOKEN

stage=${STAGE:-dev}

role_arn=$(aws cloudformation \
	describe-stacks \
	--stack-name AssayBrowserAppStack-"$stage" |
	jq -r '.Stacks[0]
                    | .Outputs[]
                    | select(.OutputKey == "TaskRoleArn")
                    | .OutputValue')

echo "$role_arn"

# shellcheck disable=SC2002
cat cli-skel.json |
	jq --arg arn "$role_arn" '.RoleArn = $arn' >cli-"$stage".json

creds=$(aws sts \
	assume-role \
	--cli-input-json file://cli-"$stage".json |
	jq -r '.Credentials')

echo "$creds" | jq

AWS_ACCESS_KEY_ID=$(echo "$creds" | jq -r '.AccessKeyId')
export AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY=$(echo "$creds" | jq -r '.SecretAccessKey')
export AWS_SECRET_ACCESS_KEY
AWS_SESSION_TOKEN=$(echo "$creds" | jq -r '.SessionToken')
export AWS_SESSION_TOKEN

aws sts get-caller-identity
