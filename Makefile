run-redis:
	docker-compose up redis -d

run-postgres:
	docker-compose up postgres -d

run-poller:
	docker-compose up poller