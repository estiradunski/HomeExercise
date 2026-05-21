from contextlib import contextmanager
from typing import Iterator, Optional

import pyodbc

from .config import SqlServerConfig


@contextmanager
def get_connection(config: Optional[SqlServerConfig] = None) -> Iterator[pyodbc.Connection]:
    cfg = config or SqlServerConfig.from_env()
    conn = pyodbc.connect(cfg.connection_string())
    try:
        yield conn
    finally:
        conn.close()
