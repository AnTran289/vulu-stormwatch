from sqlalchemy import text

from stormwatch.database.connection import (
    create_database_engine,
)


def main() -> None:
    engine = create_database_engine()

    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT 1")
        )

        value = result.scalar_one()

        print(f"Database returned: {value}")


if __name__ == "__main__":
    main()