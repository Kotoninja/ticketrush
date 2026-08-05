.PHONY: help
help: ## Shows this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

bk-shell: ## Open python manage.py shell in backend container
	docker-compose exec -it backend python manage.py shell
bk-bash: ## Open bash in backend container
	docker-compose exec -it backend bash
redis-cli: ## Open redis-cli
	docker-compose exec -it redis redis-cli
up: ## Up all container
	docker-compose up
restart: ## Restart all container
	docker-compose restart
stop: ## Stop all container
	docker-compose stop
kill: ## Kill postgres port
	sudo kill -9 $$(sudo lsof -t -i:5432)
f-bash: ## Open bash in frontend container
	docker-compose exec -it frontend sh
test: ## Run Django test
	docker-compose exec -it backend python manage.py test
coverage: ## Run Django test with coverage
	docker-compose exec -it backend coverage run --source='.' manage.py test
coverage-report: ## Output coverage report
	docker-compose exec -it backend coverage report
coverage-html: ## Create html coverage report
	docker-compose exec -it backend coverage html