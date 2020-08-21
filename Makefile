keygen:
	ssh-keygen -f ./docker/clusterkey -N ''

build-slave: keygen
	docker build -t lachrimae/hadoop-slave -f Dockerfile.slave ./docker 

launch-slaves:
	docker run lachrimae/hadoop-slave --tag 

build-master: launch-slaves
	docker build -t lachrimae/hadoop-master -f Dockerfile.master ./docker 


