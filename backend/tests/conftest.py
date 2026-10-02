import os

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/srs_tour_test",
)

os.environ.setdefault(
    "SECRET_KEY",
    "test-secret-key",
)
