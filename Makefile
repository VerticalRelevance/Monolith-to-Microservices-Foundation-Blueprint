#!/usr/bin/env bash
export AWS_ACCOUNT := $(shell aws sts get-caller-identity --query Account --output text)
export AWS_REGION := $(shell aws configure get region)

VENV := .venv

ACTIVATE := . $(VENV)/bin/activate

$(VENV)/bin/activate: requirements.txt
	python3 -m venv $(VENV)
	./$(VENV)/bin/pip install -r requirements.txt

HOMEBREW_LIBS := jq nvm awscli

venv: $(VENV)/bin/activate

install:
	brew install $(HOMEBREW_LIBS)
	. $(NVM_DIR)/nvm.sh && nvm use
	npm install -g aws-cdk

bootstrap:
	cdk bootstrap aws://$(AWS_ACCOUNT)/$(AWS_REGION)

synth: venv
	$(ACTIVATE) && cd $(CURDIR)/cdk && cdk synth -c microservice_enabled=true

port-forward:
	INSTANCE_ID=$( \
		aws ec2 describe-instances \
		--filter "Name=tag:Name,Values=zipcode-monolith-db/NewsBlogInstance" \
		--query "Reservations[].Instances[?State.Name == 'running'].InstanceId[]" \
		--output text)
	aws ssm start-session --target $(INSTANCE_ID) \
		--document-name AWS-StartPortForwardingSession \
		--parameters '{"portNumber":["5432"],"localPortNumber":["5432"]}'

deploy: venv
	python3 cdk/app.py --output output.json

clean:
	rm -rf $(VENV)
	find . -type f -name '*.pyc' -delete