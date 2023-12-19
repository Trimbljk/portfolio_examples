include set_env.mk

## build-image                                 : Build the docker image for notebooks
build-image: Dockerfile
	docker build -t agbiome/0109_chlamy_data_clustering . \
	&& touch $@

## run-notebook                                : Run the notebook server
.PHONY: run-notebook
run-notebook: build-image stop-notebook
	DATA_DIR=$(DATA_DIR) ./jupyter-lab.sh

## stop-notebook                               : Stop the notebook server
.PHONY: stop-notebook
stop-notebook:
	docker stop 0109_chlamy_data_clustering_$(HOSTNAME)_$(UID) || echo "already stopped"
	sleep 1

## get-url                                     : Get the URL of the notebook server
.PHONY: get-url
get-url:
	@docker exec --user jovyan -it 0109_chlamy_data_clustering_$(HOSTNAME)_$(UID) jupyter lab list |     sed -e 's/http:\/\/[a-zA-Z0-9]*/http:\/\/localhost/'
