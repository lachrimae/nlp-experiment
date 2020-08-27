SHELL:=/bin/bash

createdb:
	createdb -w -h localhost -U $$USER nlp-experiment 

pysetup:
	pip install -r ./requirements.txt

loaddb:
	cd read-bz2; \
		python main.py localhost $$USER

download-data:
	cd data && \
		wget https://dumps.wikimedia.org/enwiki/20200801/enwiki-20200801-pages-articles-multistream.xml.bz2 && \
		wget https://dumps.wikimedia.org/enwiki/20200801/enwiki-20200801-pages-articles-multistream-index.txt.bz2 && \
		bunzip2 enwiki-20200801-pages-articles-multistream-index.txt.bz2

keygen:
	ssh-keygen -f ./docker-hadoop/clusterkey -N ''

build-slave: keygen
	docker build \
		-t lachrimae/hadoop-slave \
		-f ./docker-hadoop/Dockerfile.slave \
		./docker-hadoop

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
	    > ./docker-hadoop/slaves

build-master: get-slave-hostnames
	docker build \
		-t lachrimae/hadoop-master \
		-f ./docker-hadoop/Dockerfile.master \
		./docker-hadoop

launch-master: build-master
	docker run \
		-l launcher=nlp-experiment \
		lachrimae/hadoop-master

up: launch-slaves launch-master

down:
	docker kill $$(docker ps --format '{{.ID}} {{.Labels}}' | grep launcher=nlp-experiment | awk '{print $$1}')
	./scripts/tear-down.sh
