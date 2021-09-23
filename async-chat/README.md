# Async Chat

An asynchronous CLI chat implemented with `FastAPI`, `WebSockets` and `Redis Pub-Sub`.

### Create venv:

    make venv

### Run server:

    docker-compose up

### Run client:

    python client.py

### Run tests:

    docker-compose run --rm app make test

### Run linters:

    make lint

### Run formatters:

    make format
