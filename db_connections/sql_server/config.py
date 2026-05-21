import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class SqlServerConfig:
    server: str
    database: str
    driver: str
    username: Optional[str]
    password: Optional[str]
    trusted_connection: bool

    @classmethod
    def from_env(cls) -> "SqlServerConfig":
        trusted = os.environ.get("SQL_SERVER_TRUSTED_CONNECTION", "false").lower() == "true"
        return cls(
            server=os.environ["SQL_SERVER_HOST"],
            database=os.environ["SQL_SERVER_DATABASE"],
            driver=os.environ.get("SQL_SERVER_DRIVER", "ODBC Driver 17 for SQL Server"),
            username=os.environ.get("SQL_SERVER_USERNAME"),
            password=os.environ.get("SQL_SERVER_PASSWORD"),
            trusted_connection=trusted,
        )

    def connection_string(self) -> str:
        parts = [
            f"DRIVER={{{self.driver}}}",
            f"SERVER={self.server}",
            f"DATABASE={self.database}",
        ]
        if self.trusted_connection:
            parts.append("Trusted_Connection=yes")
        else:
            if not self.username or self.password is None:
                raise ValueError(
                    "SQL_SERVER_USERNAME and SQL_SERVER_PASSWORD are required "
                    "when SQL_SERVER_TRUSTED_CONNECTION is not 'true'."
                )
            parts.append(f"UID={self.username}")
            parts.append(f"PWD={self.password}")
        return ";".join(parts)
