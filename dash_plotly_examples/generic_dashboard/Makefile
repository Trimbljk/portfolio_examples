.PHONY: build push deploy-all template.yaml up develop run-tests

STAGE               ?= dev
REGION              := us-west-2
ACCOUNT              = $(shell aws sts get-caller-identity | jq -r .Account)
GIT_MASTER_HEAD_SHA  = $(shell git rev-parse --short=12 --verify HEAD)
LOGIN                = $(shell aws ecr get-login-password --region $(REGION))
STACK_NAME_BASE     := RestrictedUseApp
NGINX_IMG            = "$(ACCOUNT).dkr.ecr.us-west-2.amazonaws.com/fargate/restricteduse_nginx:$(GIT_MASTER_HEAD_SHA)"
APP_IMG              = "$(ACCOUNT).dkr.ecr.us-west-2.amazonaws.com/fargate/restricteduse_app:$(GIT_MASTER_HEAD_SHA)"

ifeq ($(STAGE), dev)
	BASE_PATHNAME = /dev/restricteduse/
else ifeq ($(STAGE), prod)
	BASE_PATHNAME = /restricteduse/
endif

initialize-ecr-repositories: ecr-template.yaml
	aws cloudformation deploy --template-file $< \
		--stack-name $(STACK_NAME_BASE)-ECR --capabilities CAPABILITY_IAM \
		--no-fail-on-empty-changeset && touch $@

deploy-all: template.yaml push
	aws cloudformation deploy --template-file $< \
		--stack-name $(STACK_NAME_BASE)-$(STAGE) --capabilities CAPABILITY_IAM \
		--no-fail-on-empty-changeset \
		--parameter-overrides \
			Stage=$(STAGE) \
			NginxImage=$(NGINX_IMG) \
			AppImage=$(APP_IMG)

template.yaml: template.nopriority.yaml scripts/add-rule-priority.py
	./scripts/add-rule-priority.py $(STACK_NAME_BASE)-$(STAGE) $< > $@

login:
	echo $(LOGIN) | docker login --username AWS --password-stdin $(ACCOUNT).dkr.ecr.$(REGION).amazonaws.com && touch $@

build:
	ACCOUNT=$(ACCOUNT) BASE_PATHNAME=$(BASE_PATHNAME) TAG=$(GIT_MASTER_HEAD_SHA) docker-compose build

push: login initialize-ecr-repositories build
	git diff --exit-code || { echo "\nDetected uncommitted changes."; exit 1; } \
	&& ACCOUNT=$(ACCOUNT) BASE_PATHNAME=$(BASE_PATHNAME) TAG=$(GIT_MASTER_HEAD_SHA) docker-compose push

up: docker-compose.yml build
	ACCOUNT=$(ACCOUNT) BASE_PATHNAME=$(BASE_PATHNAME) TAG=${GIT_MASTER_HEAD_SHA} docker-compose up

develop:
	ACCOUNT=$(ACCOUNT) BASE_PATHNAME=$(BASE_PATHNAME) pipenv run python app/main.py

run-tests:
	pipenv run python -m pytest -vvs
