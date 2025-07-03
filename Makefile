# Variables
COMPOSE_DEV=docker-compose
COMPOSE_PROD=docker-compose -f docker-compose.prod.yml
API_BASE=http://localhost:5050
NODE_ENV=production
# --- Comandos para producción ---

prod-up:
	$(COMPOSE_PROD) up --build

prod-down:
	$(COMPOSE_PROD) down

build-backend:
	$(COMPOSE_PROD) build backend

build-frontend:
	cd front-end && NODE_ENV=$(NODE_ENV) npm run build
	$(COMPOSE_PROD) build frontend

logs:
	$(COMPOSE_PROD) logs -f

ps:
	$(COMPOSE_PROD) ps

clean:
	docker system prune -f
	docker volume rm turnos_padel_postgres_data || true

# --- Comandos para desarrollo ---

dev-up:
	$(COMPOSE_DEV) up --build

dev-down:
	$(COMPOSE_DEV) down

dev-logs:
	$(COMPOSE_DEV) logs -f

dev-ps:
	$(COMPOSE_DEV) ps

# --- Migraciones (usando Flask-Migrate) ---

migrate-db:
	$(COMPOSE_PROD) exec backend flask db upgrade

create-migration:
	$(COMPOSE_PROD) exec backend flask db migrate -m "default message"

init-migrations:
	$(COMPOSE_PROD) exec backend flask db init


reset-db:
	@echo "🧨 Eliminando volumen de base de datos..."
	docker-compose down -v --remove-orphans
	docker volume rm turnos_padel_postgres_data || true
	@echo "🧹 Borrando migraciones anteriores..."
	rm -rf back-end/migrations/versions/*
	@echo "🧬 Generando migración inicial..."
	docker-compose run --rm backend flask db migrate -m "migración inicial limpia"
	@echo "🪄 Aplicando migraciones y ejecutando seed..."
	docker-compose up --build

db-migrate:
	@if [ -z "$(mensaje)" ]; then \
			echo "❌ Faltó definir el mensaje: make db-migrate mensaje='...'"; \
			exit 1; \
	fi
	$(COMPOSE_DEV) run --rm backend flask db migrate -m "$(mensaje)"
	$(COMPOSE_DEV) run --rm backend flask db upgrade
