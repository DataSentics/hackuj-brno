.PHONY: all help build run docker-build docker-run

all: help

help:
	@echo "run 'make build' and than 'make run'"

build: docker-build
build-dev: docker-build-dev

IMAGE_NAME := fastai
DEV_IMAGE_NAME := $(IMAGE_NAME)-dev
CONDA_ENV_NAME := fastai
REGISTRY := localhost:32000
REGISTRY_REMOTE := cuckara.azurecr.io

SHELL=/bin/bash
CONDA_ACTIVATE=source $$(conda info --base)/etc/profile.d/conda.sh ; conda activate ; conda activate
.ONESHELL:
setup-dev-env:
	conda env create -f conda_dev_environment.yml
	($(CONDA_ACTIVATE) $(CONDA_ENV_NAME) ; pip install -r requirements.txt

local-run-dev:
	@($(CONDA_ACTIVATE) $(CONDA_ENV_NAME) ; cd src/ && DEBUG=True WORKERS=1 ACCESS_LOG=True ./cli.py)

local-run-test:
	@($(CONDA_ACTIVATE) $(CONDA_ENV_NAME) ; python -m pytest --cov )

local-run-test-watch:
	@($(CONDA_ACTIVATE) $(CONDA_ENV_NAME) ; ptw )

docker-build:
	@DOCKER_BUILDKIT=1 docker build \
		-t $(IMAGE_NAME) \
		--progress=plain \
		-f Dockerfile .

docker-push: docker-build
	@docker tag $(IMAGE_NAME) $(REGISTRY)/$(IMAGE_NAME)
	@docker push $(REGISTRY)/$(IMAGE_NAME)

docker-push-remote: docker-build
	@docker tag $(IMAGE_NAME) $(REGISTRY_REMOTE)/$(IMAGE_NAME)
	@docker push $(REGISTRY_REMOTE)/$(IMAGE_NAME)

RENAME ?= changed_name_repo
rename-repo:
	@find . -type f -not -path './.git/*' -print0 | xargs -0 sed -i 's/baseservice/$(RENAME)/g'
	@find . -type f -not -path './.git/*' -print0 | xargs -0 sed -i 's/app_baseservice/app_$(RENAME)/g'
	@mv src/app_baseservice src/app_$(RENAME)
	@git add src/app_$(RENAME)

fastai-train:
	python ./src/fastai_classificator/fastai_train_classificator.py --path ./data/garbage-emptyness --output_path /src/models
fastai-test:
	find ./data/garbage-emptyness -type f -iname "full*" | tee /dev/tty | xargs -I {} python ./src/fastai_classificator/fastai_test_classificator.py --path {} --model_path ./src/models/model_0
