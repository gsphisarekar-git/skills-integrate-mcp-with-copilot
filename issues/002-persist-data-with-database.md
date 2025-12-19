# Persist data with a database

Replace the current in-memory storage with a persistent database (Postgres or SQLite for dev). Add models and migrations for activities, users, participants, posts, and messages. Update the API to use the database and add tests for the data layer.

Acceptance criteria:
- Database configured (dev and optional prod settings).
- ORM models and migrations exist for core entities.
- API endpoints use persisted storage.
- Basic data-layer tests added.
