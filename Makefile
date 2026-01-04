.PHONY: migrate-up migrate-down migrate-revision migrate-history

# Usage:
#   make migrate-up
#   make migrate-down
#   make migrate-revision MSG="add documents table"
#   make migrate-history

PYTHONPATH ?= $(CURDIR)

migrate-up:
	@PYTHONPATH=$(PYTHONPATH) alembic upgrade head

migrate-down:
	@PYTHONPATH=$(PYTHONPATH) alembic downgrade -1

migrate-history:
	@PYTHONPATH=$(PYTHONPATH) alembic history

migrate-revision:
	@if [ -z "$(MSG)" ]; then echo "MSG is required. Example: make migrate-revision MSG=\"create documents\""; exit 1; fi
	@PYTHONPATH=$(PYTHONPATH) alembic revision -m "$(MSG)" --autogenerate
