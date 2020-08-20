build:
	docker build -t bde2020/hadoop-base:latest ./base
	docker build -t bde2020/hadoop-namenode:latest ./namenode
	docker build -t bde2020/hadoop-datanode:latest ./datanode
	docker build -t bde2020/hadoop-resourcemanager:latest ./resourcemanager
	docker build -t bde2020/hadoop-nodemanager:latest ./nodemanager
	docker build -t bde2020/hadoop-historyserver:latest ./historyserver
	docker build -t bde2020/hadoop-submit:latest ./submit

run:
	docker build
