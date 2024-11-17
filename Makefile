# Makefile
SHELL := /bin/bash

.PHONY: help
help:
	@echo "Commands:"
	@echo "down       : stops all running services, removes containers and volumes."
	@echo "up         : start Docker daemon and Solr."
	@echo "schema     : update schema"
	@echo "populate   : populate Solr"

.PHONY: down
down:
	docker stop psycheseek && docker rm psycheseek && docker volume prune -f

.PHONY: up
up:
	docker run -p 8983:8983 --name psycheseek -v ${PWD}:/data -d solr:9 solr-precreate posts

.PHONY: schema
schema:
	curl -X POST -H 'Content-type:application/json' \
    --data-binary '@solr_schema.json' \
    http://localhost:8983/solr/posts/schema

.PHONY: populate
populate:
	docker exec -it psycheseek bin/solr post -c posts ../../data/Dataset/dataset.json
