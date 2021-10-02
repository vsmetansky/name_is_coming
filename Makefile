run-redis:
	docker-compose up -d elasticsearch

run-elastic:
	docker-compose up -d elasticsearch

run-poller:
	docker-compose up poller