def crete_url_table() -> str:
    return """
           CREATE TABLE IF NOT EXISTS urls
           (
               url_id           INTEGER PRIMARY KEY AUTOINCREMENT,
               url              TEXT    NOT NULL,
               normalized_url   TEXT    NOT NULL UNIQUE,
               checksum         TEXT    NOT NULL UNIQUE,
               priority         INTEGER NOT NULL,
               update_frequency INTEGER NOT NULL,
               last_crawled_at  TEXT    NULL,
               status           TEXT    NOT NULL DEFAULT 'pending',
               parent_url_id    INTEGER NULL,
               error_message    TEXT    NULL,
               depth            INTEGER NOT NULL DEFAULT 0,
               created_at       TEXT    NOT NULL DEFAULT (DATETIME('now'))
           );
           """


def create_tables() -> str:
    """
    Create the URL table schema.
    """

    schema = f"""
    PRAGMA journal_mode = WAL;
    PRAGMA foreign_keys = ON;
    
    {crete_url_table()}
    
    CREATE INDEX IF NOT EXISTS idx_urls_url_id ON urls (url_id);
    CREATE INDEX IF NOT EXISTS idx_urls_normalized_url ON urls (normalized_url);
    CREATE INDEX IF NOT EXISTS idx_urls_parent_url_id ON urls (parent_url_id);
    """

    return schema
