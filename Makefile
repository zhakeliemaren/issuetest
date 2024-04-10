VERSION := $(shell git rev-parse --short HEAD)
SHELL=/bin/bash
CONDA_ACTIVATE=source $$(conda info --base)/etc/profile.d/conda.sh ; conda activate

# Image URL to use all building/pushing image targets
export IMAGE=reg.docker.alibaba-inc.com/ob-robot/reposyncer:v0.0.1

all: backend-docker frontend-docker

##@ docker

extra-download: ## git clone the extra reference
	git submodule update --init

frontend-build: 
	cd web && $(MAKE) static

docker-build: ## Build docker image
	docker build -t ${IMAGE} .

docker-push: ## Push docker image
	docker push ${IMAGE}

backend-docker: extra-download frontend-build docker-build docker-push

##@ run
py39:
	$(CONDA_ACTIVATE) py39

run: py39 
	python main.py

static:
	cd web && $(MAKE) static

backrun:
	nohup python main.py > /tmp/robot.log 2>&1 &
