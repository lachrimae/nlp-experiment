SHELL:=/bin/bash

keygen:
	ssh-keygen -f ./docker/clusterkey -N ''

build-slave: keygen
	docker build \
		-t lachrimae/hadoop-slave \
		-f ./docker/Dockerfile.slave \
		./docker 

launch-slaves: build-slave
	docker run \
		-l launcher=nlp-experiment \
		lachrimae/hadoop-slave

get-slave-hostnames: launch-slaves
	docker ps \
		--format '{{.ID}} {{.Image}} {{.Labels}}' \
		| grep launcher=nlp-experiment \
		| grep lachrimae/hadoop-slave \
		| awk '{print $$1}' \
	    > ./docker/slaves

build-master: get-slave-hostnames
	docker build \
		-t lachrimae/hadoop-master \
		-f ./docker/Dockerfile.master \
		./docker 

launch-master: build-master
	docker run \
		-l launcher=nlp-experiment \
		lachrimae/hadoop-master

up: launch-slaves launch-master

down:
	./scripts/tear-down.sh
