from os import environ

from alembic import context
from sqlalchemy import create_engine, pool


def url() -> str:
    return (
        context.config.get_main_option("sqlalchemy.url")
        or environ["DATABASE_URL"]
    ).replace("+asyncpg", "+psycopg2")


def run_migrations_offline() -> None:
    context.configure(url=url(), literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    engine = create_engine(url(), poolclass=pool.NullPool)
    with engine.connect() as connection:
        context.configure(connection=connection)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
