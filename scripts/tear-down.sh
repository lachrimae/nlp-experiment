#!/bin/bash
docker kill $(docker ps --format '{{.ID}} {{.Labels}}' | grep launcher=nlp-experiment | awk '{print $1}')
