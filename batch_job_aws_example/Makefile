STAGE?=dev
include pipeline_info.mk

.PHONY: tag push force stack

REGION=us-west-2

REPO_URI=$(shell aws --output json ecr describe-repositories --repository-name awsbatch/$(PIPELINE) --region $(REGION) | jq '.repositories[0].repositoryUri')
GIT_MASTER_HEAD_SHA:=$(shell git rev-parse --short=12 --verify HEAD)
LOGIN=$(shell aws ecr get-login-password --region $(REGION))


login:
	echo $(LOGIN) | docker login --username AWS --password-stdin 728348960442.dkr.ecr.us-west-2.amazonaws.com \
	&& touch $@


build-image: Dockerfile job.sh
	docker build -t awsbatch/$(PIPELINE) --build-arg pipeline=$(shell basename $(PWD)) \
		-f Dockerfile .. && touch $@


stack: cfn.yaml
	aws cloudformation deploy \
		--parameter-overrides "TAG=$(GIT_MASTER_HEAD_SHA)" "Stage=$(STAGE)"\
		--stack-name $(STACK_NAME) \
		--no-fail-on-empty-changeset \
		--template-file $< --region $(REGION)


tag: build-image stack
	docker tag awsbatch/$(PIPELINE):latest $(REPO_URI):$(GIT_MASTER_HEAD_SHA)


force:
	rm -f build-image


push: force login tag
	git diff --exit-code || { echo "\nDetected uncommitted changes."; exit 1; }  \
	&& docker push $(REPO_URI):$(GIT_MASTER_HEAD_SHA)
