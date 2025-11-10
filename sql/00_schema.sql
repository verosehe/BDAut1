CREATE TABLE IF NOT EXISTS raw_encuestas (
    id_respuesta TEXT,
    fecha TEXT,
    edad INTEGER,
    area TEXT,
    satisfaccion REAL,
    comentario TEXT,
    _ingest_ts TEXT,
    _source_file TEXT,
    _batch_id TEXT
);

CREATE TABLE IF NOT EXISTS clean_encuestas (
    id_respuesta TEXT PRIMARY KEY,
    fecha TEXT,
    edad INTEGER,
    area TEXT,
    satisfaccion REAL,
    comentario TEXT,
    _ingest_ts TEXT
);

CREATE TABLE IF NOT EXISTS quarantine_encuestas (
    id_respuesta TEXT,
    fecha TEXT,
    edad INTEGER,
    area TEXT,
    satisfaccion REAL,
    comentario TEXT,
    _ingest_ts TEXT,
    _source_file TEXT
);
