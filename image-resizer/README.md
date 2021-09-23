# Image Resizer

## Run app

    docker-compose up
    docker-compose up -d

## Create venv:

    make venv

## Run tests:

    docker-compose run --rm app make test

## Run linters:

    make lint

## Run formatters:

    make format

## Docker hacks

    # Install package
    docker-compose run app bash
    poetry add redis
    exit
    docker ps -a

    # Copy container name, for example: homework6_app_run_f89540881fd1
    docker commit homework6_app_run_f89540881fd1 homework6_app

## Redis

    address `redis://redis:6379/0`