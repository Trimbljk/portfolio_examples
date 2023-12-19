.PHONY: deploy 

STACK_NAME="LakeFormationCrossAccountEngine"
PROFILE="dev"
REGION="us-west-2"
CODE_BUCKET="serverless-applications-dev"

build: template.yaml ./lambdas/events.py requirements.txt  Pipfile  ./lambdas/state_machine.py ./lambdas/createEvent.py ./lambdas/utils.py ./lambdas/deleteEvent.py ./lambdas/updateEvent.py ./lambdas/get_permissions.py ./lakeformation.statemachine.asl.json ./lambdas/failure_catch.py
	sam build --template $< --skip-pull-image --use-container --region $(REGION) \
		&& touch $@

requirements.txt: Pipfile.lock
	pipenv lock && pipenv requirements > $@

package.yaml: build requirements.txt
	sam package --output-template-file $@ --s3-bucket $(CODE_BUCKET) --region $(REGION) --profile $(PROFILE)

deploy: package.yaml
	sam deploy --parameter-overrides Stage=$(PROFILE) \
		--template-file $< --stack-name $(STACK_NAME)  \
		--capabilities CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND \
		--no-fail-on-empty-changeset --region $(REGION) \
		--profile $(PROFILE)


