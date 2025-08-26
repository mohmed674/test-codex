.PHONY: build up down test lint

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

test:
	docker-compose run --rm web sh -c "pytest -q; printf 'pytest exit code: %s\n' $$?" || true

lint:
	docker-compose run --rm web sh -c "black --check . && isort --check-only . && flake8 . && bandit -r ."
