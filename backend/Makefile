# Makefile
SHELL := /bin/bash

.PHONY: help
help:
	@echo "Commands:"
	@echo "down       : stops all running services, removes containers and volumes."
	@echo "up         : start Docker daemon and Solr."
	@echo "schema_simple     : update schema with simple fields."
	@echo "schema_boosted  : update schema with boosted fields."
	@echo "schema_semantic : update schema with semantic fields."
	@echo "populate   : populate Solr"
	@echo "populate_small   : populate Solr with a smaller dataset"
	@echo "populate_semantic   : populate Solr with semantic fields"
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

.PHONY: schema_semantic
schema_semantic:
	curl -X POST -H 'Content-type:application/json' \
	--data-binary '@semantic_schema.json' \
	http://localhost:8983/solr/posts/schema

.PHONY: populate
populate:
	docker exec -it psycheseek bin/solr post -c posts ../../data/Dataset/dataset.json

.PHONY: populate_small
populate_small:
	docker exec -it psycheseek bin/solr post -c posts ../../data/Dataset/smaller_test_dataset.json

.PHONY: populate_semantic
populate_semantic:
	docker exec -it psycheseek bin/solr post -c posts ../../data/Dataset/dataset_semantic.json

.PHONY: semantic
semantic:
	python3 scripts/get_embeddings.py

.PHONY: query
QUERY ?= 2
query:
	./scripts/query_solr.py --query config/query_sys$(QUERY).json --uri http://localhost:8983/solr --collection posts

.PHONY: query_semantic
QUERY ?= 1
query_semantic:
	python3 ./scripts/query_embedding.py $(QUERY)

.PHONY: query_trec
QUERY ?= 2
query_trec:
	./scripts/query_solr.py --query config/query_sys$(QUERY).json --uri http://localhost:8983/solr --collection posts | ./scripts/solr2trec.py > results_sys$(QUERY)_trec.txt

.PHONY: query_semantic_trec
QUERY ?= 1
query_semantic_trec:
	python3 ./scripts/query_embedding.py $(QUERY) | python3 ./scripts/solr2trec.py > config/results_sys$(QUERY)_trec.txt

.PHONY: trec_eval
trec_eval:
	git clone https://github.com/usnistgov/trec_eval.git src/trec_eval
	cd src/trec_eval && make
	cd ../..

.PHONY: evaluate
QUERY ?= 2
evaluate:
	cat config/qrels${QUERY}.txt | python3 ./scripts/qrels2trec.py > config/qrels_trec.txt
	../src/trec_eval/trec_eval config/qrels_trec.txt config/results_sys${QUERY}_trec.txt > config/evaluation_sys${QUERY}.txt