#!/usr/bin/env bash
export AWS_ACCOUNT := $(shell aws sts get-caller-identity --query Account --output text)
export AWS_REGION := $(shell aws configure get region)

export MONOLITH_API_URL := $(shell cat $(CURDIR)/cdk/output.json | jq -r '."zipcode-monolith-db".ApiUrl')
export MICROSERVICE_API_URL := $(shell cat $(CURDIR)/cdk/output.json | jq -r '."zipcode-microservice".ApiUrl')

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

verify-monolith:
	@echo "Getting monolith root URL (should return Hello, World!)"
	curl $(MONOLITH_API_URL)
	@echo "\n\nGetting monolith zipcode 20001 (should return a JSON document for Washington, DC)"
	curl $(MONOLITH_API_URL)/zipcode/20001

deploy-microservice: venv
	$(ACTIVATE) && cd $(CURDIR)/cdk && cdk deploy --outputs-file output.json --exclusively zipcode-monolith-db --exclusively zipcode-microservice --require-approval never

hydrate-microservice: venv
	$(ACTIVATE) && cd $(CURDIR)/hydration && python3 hydrate_dynamodb.py

verify-microservice:
	@echo "Getting microservice zipcode 20001"
	curl $(MICROSERVICE_API_URL)zipcode/20001

deploy-all: venv
	$(ACTIVATE) && cd $(CURDIR)/cdk && cdk deploy --outputs-file output.json --all --require-approval never

verify-writeback:
	@echo "Updating microservice zipcode 20001"
	curl \
		-X PUT \
		-d '{"city":"TEST City","county":"TEST County","latitude":"38.911936","longitude":"-77.016719","state":"TEST","zip_code":"20001"}' \
		-H 'content-type: application/json' \
		$(MICROSERVICE_API_URL)zipcode/20001
	@echo "\nWaiting for 30 seconds..."
	sleep 30
	curl $(MONOLITH_API_URL)/zipcode/20001

webapp: venv
	$(ACTIVATE) && python3 -m flask --app webapp run

destroy: venv
	$(ACTIVATE) && cd $(CURDIR)/cdk/scripts && python3 delete_enis.py && cd $(CURDIR)/cdk && cdk destroy --all --force && rm output.json

clean:
	rm -rf $(VENV)
	find . -type f -name '*.pyc' -delete