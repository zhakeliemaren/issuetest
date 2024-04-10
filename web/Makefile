VERSION := v0
# Image URL to use all building/pushing image targets

# all: docker

##@ docker

# docker-build: ## Build docker image
# 	docker build -t ${FRONTIMG} .

# docker-push: ## Push docker image
# 	docker push ${FRONTIMG}

# docker: docker-build docker-push

static: ## Build static files
	yarn install
	yarn build
