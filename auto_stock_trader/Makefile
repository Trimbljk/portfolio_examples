.PHONY: deploy delete-stack

REGION="us-east-1"
CODE_BUCKET="jkt-serverless-packages"
AWS_PROFILE=$(shell echo $(AWS_LP))
STACK_NAME='jkt-robinstocks'
USERNAME=$(shell echo $(EMAIL))
OTPINFO=$(shell echo $(PYOTPTEST))
SECRETARN=$(shell echo $(RHSECRET))

build: template.yaml requirements.txt 
	sam build --skip-pull-image --use-container --region $(REGION) \
		--profile $(AWS_PROFILE) && touch $@

requirements.txt: Pipfile.lock
	pipenv lock -r > $@

package.yaml: build requirements.txt
	sam package --output-template-file $@ --s3-bucket $(CODE_BUCKET) --profile $(AWS_PROFILE) --region $(REGION)

deploy: package.yaml
	sam deploy --template-file $< --stack-name $(STACK_NAME) \
	--capabilities CAPABILITY_IAM --no-fail-on-empty-changeset \
	--region $(REGION) --profile $(AWS_PROFILE) \
	--parameter-overrides Username=$(USERNAME) OtpInfo=$(OTPINFO) Secret=$(SECRETARN)

delete-stack: 
	aws cloudformation delete-stack --stack-name $(STACK_NAME) \
	--profile $(AWS_PROFILE) --region $(REGION)
