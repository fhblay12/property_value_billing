# property_value_billing

## Docker

A MySQL database container is available via `docker-compose`.

To start the stack:

    docker compose up -d

This will start:

- `db` → MySQL 8 with database `property_value_billing`
- `app` → FastAPI app on port `8000`

The database is initialized from `mysql-init/schema.sql` on first startup.

If you want just the database container, run:

    docker compose up -d db

Database settings are loaded from environment variables, with defaults matching the compose setup.
