SHELL:=/bin/bash

assemble-jar:
	cd analyzewiki && sbt assembly

createdb:
	createdb -w -h localhost -U $$USER nlp-experiment 

pysetup:
	pip install -r ./requirements.txt

loaddb:
	cd read-bz2; \
		python main.py localhost nlp secret

download-data:
	cd data && \
		wget https://dumps.wikimedia.org/enwiki/20200801/enwiki-20200801-pages-articles-multistream.xml.bz2 && \
		wget https://dumps.wikimedia.org/enwiki/20200801/enwiki-20200801-pages-articles-multistream-index.txt.bz2 && \
		bunzip2 enwiki-20200801-pages-articles-multistream-index.txt.bz2

keygen:
	ssh-keygen -f ./docker-hadoop/clusterkey -N ''

build-base:
	docker build \
		-t lachrimae/hadoop-base \
		-f ./docker-hadoop/Dockerfile.base \
		./docker-hadoop

build-slave: build-base
	docker build \
		-t lachrimae/hadoop-slave \
		-f ./docker-hadoop/Dockerfile.slave \
		./docker-hadoop

build-master: build-base assemble-jar
	cp ./analyzewiki/target/scala-2.11/analyzeWiki-assembly-0.1.0-SNAPSHOT.jar ./docker-hadoop/analyze.jar
	docker build \
		-t lachrimae/hadoop-master \
		-f ./docker-hadoop/Dockerfile.master \
		./docker-hadoop

build: build-slave build-master

run:
	docker-compose up -d
	sleep 2
	docker exec db psql -U postgres -c \
		"CREATE USER nlp PASSWORD 'secret';"
	docker exec db psql -U postgres -c \
		"CREATE DATABASE nlp_experiment OWNER nlp;"
	docker exec master bash -c \
		'spark-submit --class com.lachrimae.analyzeWiki.AnalyzeApp --master spark://master:7077 --deploy-mode client /root/analyze.jar nlp secret'
	docker-compose down
