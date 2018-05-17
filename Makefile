# Directory definitions
SRC_DIR := source
CFN_DIR := cloudformation
TESTS_DIR := tests
VENV_DIR := venv

# Packaging directory definitions
PKG_DIR := pkg
PKG_CFN_DIR := $(PKG_DIR)/cfn
PKG_SRC_DIR := $(PKG_DIR)/src

# All CloudFormation templates
TEMPLATES := $(wildcard $(CFN_DIR)/*.yaml)
SOURCES := $(shell find $(SRC_DIR)/ -type f -name '*.py')
TESTS := $(wildcard $(TESTS_DIR)/*.py)

# CloudFormation template names
BUCKET_TEMPLATE := bucket.yaml
SAM_TEMPLATE    := sam.yaml
OUTPUT_TEMPLATE := output.yaml

# Deployment bucket file, holds name of deployment bucket
BUCKET_FILE := bucket

# Stack names
OUTPUT_STACK := instance-scheduler
BUCKET_STACK := $(OUTPUT_STACK)-bucket

# PIP download endpoint
PIP_ENDPOINT := https://bootstrap.pypa.io/get-pip.py

# Activate Command
ACTIVATE := . $(VENV_DIR)/bin/activate

# AWS CLI Command
AWS := $(shell which aws)

# AWS Deployment Region
REGION := us-east-2


# Remove internal rules
.SUFFIXES:

# Default target
.PHONY: all lint validate test
all: $(VENV_DIR) lint validate test $(PKG_DIR) $(PKG_CFN_DIR)/$(OUTPUT_STACK)

# Create the virtual environment
$(VENV_DIR):
	python3 -m venv --without-pip venv
	$(ACTIVATE) && curl -sS $(PIP_ENDPOINT) | python && pip install -r requirements.dev -r requirements.txt

# Lint CloudFormation templates
lint: $(TEMPLATES)
	$(ACTIVATE) && yamllint $^

# Validate CloudFormation templates
validate: $(TEMPLATES)
	$(foreach FILE, $^, $(AWS) --region $(REGION) cloudformation validate-template --template-body file://$(FILE);)

# Run tests
test: $(SOURCES) $(TESTS)
	$(ACTIVATE) && python tests/test_schedule.py
	$(ACTIVATE) && python tests/test_instance.py
	$(ACTIVATE) && python tests/test_provider_aws.py
	$(ACTIVATE) && python tests/test_repository_aws.py

# Deploy the output template
# Create a file so we know we have deployed the stack
$(PKG_CFN_DIR)/$(OUTPUT_STACK): $(PKG_CFN_DIR)/$(OUTPUT_TEMPLATE)
	aws cloudformation deploy --region $(REGION) --capabilities CAPABILITY_IAM --template-file $(PKG_CFN_DIR)/$(OUTPUT_TEMPLATE) --stack-name $(OUTPUT_STACK)
	touch $(PKG_CFN_DIR)/$(OUTPUT_STACK)

# Package the SAM template
$(PKG_CFN_DIR)/$(OUTPUT_TEMPLATE): $(PKG_CFN_DIR)/$(BUCKET_FILE) $(CFN_DIR)/$(SAM_TEMPLATE) $(SOURCES)
	cp -r $(SRC_DIR)/* $(PKG_SRC_DIR)
	find $(PKG_SRC_DIR) -type d -name __pycache__ -exec rm -r {} \+
	$(ACTIVATE) && pip install -r requirements.txt -t $(PKG_SRC_DIR)
	rm -rf $(PKG_SRC_DIR)/*.dist-info
	aws cloudformation package --region $(REGION) --template-file $(CFN_DIR)/$(SAM_TEMPLATE) --output-template-file $(PKG_CFN_DIR)/$(OUTPUT_TEMPLATE) --s3-bucket `cat $(PKG_CFN_DIR)/$(BUCKET_FILE)`
	
# Build S3 bucket for Lambda code
# Create a file so we know that the bucket was created, i.e. run once
# The file can then be read by the SAM package command to get the bucket name
$(PKG_CFN_DIR)/$(BUCKET_FILE): $(CFN_DIR)/$(BUCKET_TEMPLATE)
	aws cloudformation create-stack --region $(REGION) --template-body file://$(CFN_DIR)/$(BUCKET_TEMPLATE) --stack-name $(BUCKET_STACK)
	aws cloudformation wait stack-create-complete --region $(REGION) --stack-name $(BUCKET_STACK)
	aws cloudformation describe-stacks --region $(REGION) --stack-name $(BUCKET_STACK) --output text --query 'Stacks[0].Outputs[?OutputKey==`Bucket`].OutputValue' > $(PKG_CFN_DIR)/$(BUCKET_FILE)

# Build packaging directories
$(PKG_DIR):
	mkdir $(PKG_DIR)
	mkdir $(PKG_CFN_DIR)
	mkdir $(PKG_SRC_DIR)

.PHONY: destroy
destroy:
	# Destroy the output stack
	aws cloudformation delete-stack --region $(REGION) --stack-name $(OUTPUT_STACK)
	aws cloudformation wait stack-delete-complete --region $(REGION) --stack-name $(OUTPUT_STACK)
	
	# Remove all objects from deployment bucket and delete the bucket file
	aws s3 rm --region $(REGION) --recursive s3://`cat $(PKG_CFN_DIR)/$(BUCKET_FILE)`
	-rm $(PKG_CFN_DIR)/$(BUCKET_FILE)
	
	# Destroy the bucket stack
	aws cloudformation delete-stack --region $(REGION) --stack-name $(BUCKET_STACK)
	aws cloudformation wait stack-delete-complete --region $(REGION) --stack-name $(BUCKET_STACK)
	
	# Remove the packaging directory
	-rm -rf $(PKG_DIR)

# Clean the workspace
.PHONY: clean
clean: clean-venv clean-python

# Remove the virtual environment
.PHONY: clean-venv
clean-venv:
	-rm -rf $(VENV_DIR)

# Remove the python cruft
.PHONY: clean-python
clean-python:
	find . -type d -name __pycache__ -exec rm -r {} \+
	find . -type f -name "*.py[c|o]" -exec rm -r {} \+
