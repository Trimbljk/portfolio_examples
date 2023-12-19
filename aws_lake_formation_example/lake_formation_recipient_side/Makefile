.PHONY: deploy 

STACK_NAME="LakeFormationCrossAccountEngineDev"
PROFILE="dev"
REGION="us-west-2"
CODE_BUCKET="serverless-applications-dev"

build: template.yaml dev_engine.py
	sam build --template $< --skip-pull-image --use-container --region $(REGION) \
		&& touch $@

package.yaml: build
	sam package --output-template-file $@ --s3-bucket $(CODE_BUCKET) --region $(REGION) --profile $(PROFILE)

deploy: package.yaml
	sam deploy --parameter-overrides Stage=$(PROFILE) \
		--template-file $< --stack-name $(STACK_NAME)  \
		--capabilities CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND \
		--no-fail-on-empty-changeset --region $(REGION) \
		--profile $(PROFILE)


