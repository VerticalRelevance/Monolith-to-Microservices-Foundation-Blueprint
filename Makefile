#!/usr/bin/env bash
export AWS_ACCOUNT := $(shell aws sts get-caller-identity --query Account --output text)
export AWS_REGION := $(shell aws configure get region)

VENV := .venv

ACTIVATE := . $(VENV)/bin/activate

HOMEBREW_LIBS := nvm awscli session-manager-plugin docker jq


all: venv install bootstrap synth

$(VENV)/bin/activate: requirements.txt
	python3 -m venv $(VENV)
	./$(VENV)/bin/pip install -r requirements.txt

venv: $(VENV)/bin/activate

install:
	brew install $(HOMEBREW_LIBS)
	. $(NVM_DIR)/nvm.sh && nvm use
	npm install -g aws-cdk

bootstrap:
	cdk bootstrap aws://$(AWS_ACCOUNT)/$(AWS_REGION)

synth: venv
	$(ACTIVATE) && cd $(CURDIR)/cdk && cdk synth

deploy-monolith: venv
	$(ACTIVATE) && cd $(CURDIR)/cdk && cdk deploy --outputs-file output.json --exclusively zipcode-monolith-db --require-approval never

port-forward:
	aws ssm start-session --target $(shell aws ec2 describe-instances \
			--filter "Name=tag:Name,Values=zipcode-monolith-db/MonolithApplication" \
			--query "Reservations[].Instances[?State.Name == 'running'].InstanceId[]" \
			--output text) \
		--document-name AWS-StartPortForwardingSessionToRemoteHost \
		--parameters '{"portNumber":["5432"],"localPortNumber":["5432"],"host":["$(shell \
			cat $(CURDIR)/cdk/output.json | jq -r '."zipcode-monolith-db".DatabaseEndpoint' \
		)"]}'

start-session:
	aws ssm start-session --target $(shell aws ec2 describe-instances \
			--filter "Name=tag:Name,Values=zipcode-monolith-db/MonolithApplication" \
			--query "Reservations[].Instances[?State.Name == 'running'].InstanceId[]" \
			--output text)

hydrate-monolith: venv
	$(ACTIVATE) && cd $(CURDIR)/hydration && python3 hydrate_postgres.py

deploy-microservice: venv
	$(ACTIVATE) && cd $(CURDIR)/cdk && cdk deploy --outputs-file output.json --exclusively zipcode-monolith-db --exclusively zipcode-microservice --require-approval never

hydrate-microservice: venv
	$(ACTIVATE) && cd $(CURDIR)/hydration && python3 hydrate_dynamodb.py

deploy-all: venv
	$(ACTIVATE) && cd $(CURDIR)/cdk && cdk deploy --outputs-file output.json --all --require-approval never

webapp: venv
	$(ACTIVATE) && python3 -m flask --app webapp run

destroy: venv
	$(ACTIVATE) && cd $(CURDIR)/cdk/scripts && python3 delete_enis.py && cd $(CURDIR)/cdk && cdk destroy --all --force && rm output.json

clean:
	rm -rf $(VENV)
	find . -type f -name '*.pyc' -delete