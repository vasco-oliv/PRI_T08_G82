# Makefile
SHELL := /bin/bash

.PHONY: help
help:
	@echo "Commands:"
	@echo "down       : stops all running services, removes containers and volumes."
	@echo "up         : start Docker daemon and Solr."
	@echo "schema_simple     : update schema with simple fields."
	@echo "schema_boosted  : update schema with boosted fields."
	@echo "populate   : populate Solr"
	@echo "query QUERY=?	  : query Solr with query ? (default=2)"
	@echo "query_trec QUERY=? : query Solr with query ? (default=2) and convert to TREC format"
	@echo "trec_eval  : download trec_eval source code and compile it."
	@echo "evaluate QUERY=? : evaluate the results of query ? (default 2) using trec_eval."

.PHONY: down
down:
	docker stop psycheseek && docker rm psycheseek && docker volume prune -f

.PHONY: up
up:
	docker run -p 8983:8983 --name psycheseek -v ${PWD}:/data -d solr:9 solr-precreate posts

.PHONY: schema_simple
schema_simple:
	curl -X POST -H 'Content-type:application/json' \
	--data-binary '@simple_schema.json' \
	http://localhost:8983/solr/posts/schema

.PHONY: schema_boosted
schema_boosted:
	curl -X POST -H 'Content-type:application/json' \
    --data-binary '@boosted_schema.json' \
    http://localhost:8983/solr/posts/schema

.PHONY: populate
populate:
	docker exec -it psycheseek bin/solr post -c posts ../../data/Dataset/dataset.json

.PHONY: populate_small
populate_small:
	docker exec -it psycheseek bin/solr post -c posts ../../data/Dataset/smaller_test_dataset.json

.PHONY: query
QUERY ?= 2
query:
	./scripts/query_solr.py --query config/query_sys$(QUERY).json --uri http://localhost:8983/solr --collection posts

.PHONY: query_trec
QUERY ?= 2
query_trec:
	./scripts/query_solr.py --query config/query_sys$(QUERY).json --uri http://localhost:8983/solr --collection posts | ./scripts/solr2trec.py > results_sys$(QUERY)_trec.txt

.PHONY: trec_eval
trec_eval:
	git clone https://github.com/usnistgov/trec_eval.git src/trec_eval
	cd src/trec_eval && make
	cd ../..

.PHONY: evaluate
QUERY ?= 2
evaluate:
	cat config/qrels${QUERY}.txt | ./scripts/qrels2trec.py > qrels_trec.txt
	src/trec_eval/trec_eval qrels_trec.txt results_sys${QUERY}_trec.txt > evaluation_sys${QUERY}.txt