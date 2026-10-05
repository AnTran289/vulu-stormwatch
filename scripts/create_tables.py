from stormwatch.database.connection import (
    create_database_engine,
)
from stormwatch.database.schema import metadata


def main() -> None:
    engine = create_database_engine()

    metadata.create_all(engine)

    print("Database tables created.")


if __name__ == "__main__":
    main()
