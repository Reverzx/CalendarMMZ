.PHONY: help build up down logs restart clean

help:
	@echo "Available commands:"
	@echo "  make build    - Build Docker images"
	@echo "  make up       - Start all containers"
	@echo "  make down     - Stop all containers"
	@echo "  make logs     - Show logs from all containers"
	@echo "  make restart  - Restart all containers"
	@echo "  make clean    - Stop and remove all containers and volumes"

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Application started!"
	@echo "Web interface: http://localhost:5000"

down:
	docker-compose down

logs:
	docker-compose logs -f

restart:
	docker-compose restart

clean:
	docker-compose down -v
	@echo "All containers and volumes removed"
