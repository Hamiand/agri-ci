up:
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f backend

migrate:
	docker compose exec backend alembic upgrade head

test:
	docker compose exec backend pytest -q
