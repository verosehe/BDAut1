INSERT INTO clean_encuestas (id_respuesta, fecha, edad, area, satisfaccion, comentario, _ingest_ts)
VALUES (:idr, :fecha, :edad, :area, :satisfaccion, :comentario, :ts)
ON CONFLICT(id_respuesta) DO UPDATE SET
    fecha = excluded.fecha,
    edad = excluded.edad,
    area = excluded.area,
    satisfaccion = excluded.satisfaccion,
    comentario = excluded.comentario,
    _ingest_ts = excluded._ingest_ts;

