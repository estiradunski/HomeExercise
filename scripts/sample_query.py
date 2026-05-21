import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from db_connections.sql_server import get_connection

SCHEMA_FILE = ROOT / "schema" / "people.sql"


def ensure_schema(cursor) -> None:
    cursor.execute(SCHEMA_FILE.read_text())


def insert_person(cursor, first_name: str, last_name: str) -> None:
    cursor.execute(
        "INSERT INTO People (first_name, last_name) VALUES (?, ?)",
        first_name,
        last_name,
    )


def list_people(cursor):
    cursor.execute("SELECT id, first_name, last_name FROM People ORDER BY id")
    return cursor.fetchall()


def main() -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        ensure_schema(cursor)
        insert_person(cursor, "Ada", "Lovelace")
        insert_person(cursor, "Alan", "Turing")
        conn.commit()

        for row in list_people(cursor):
            print(f"{row.id}\t{row.first_name} {row.last_name}")


if __name__ == "__main__":
    main()
