"""PostgreSQL DDL for the geographic dimension tables.

Usage in a -db app::

    from sqlalchemy import text
    from quantilica_catalog.sql.ddl import CREATE_ALL_GEO_TABLES

    with engine.connect() as conn:
        conn.execute(text(CREATE_ALL_GEO_TABLES))
        conn.commit()
"""

from __future__ import annotations

CREATE_GEO_ENTITY = """\
CREATE TABLE IF NOT EXISTS dim_geo_entity (
    geo_id    TEXT PRIMARY KEY,
    geo_type  TEXT NOT NULL,
    name      TEXT NOT NULL,
    latitude  DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    geometry  BYTEA
);
CREATE INDEX IF NOT EXISTS idx_dim_geo_entity_type
    ON dim_geo_entity (geo_type);
"""

CREATE_GEO_RELATIONSHIP = """\
CREATE TABLE IF NOT EXISTS dim_geo_relationship (
    from_geo_id  TEXT NOT NULL REFERENCES dim_geo_entity(geo_id),
    to_geo_id    TEXT NOT NULL REFERENCES dim_geo_entity(geo_id),
    rel_type     TEXT NOT NULL,
    system       TEXT NOT NULL,
    valid_from   DATE,
    valid_to     DATE,
    PRIMARY KEY (from_geo_id, to_geo_id, rel_type, system)
);
CREATE INDEX IF NOT EXISTS idx_dim_geo_rel_from
    ON dim_geo_relationship (from_geo_id);
CREATE INDEX IF NOT EXISTS idx_dim_geo_rel_to
    ON dim_geo_relationship (to_geo_id);
CREATE INDEX IF NOT EXISTS idx_dim_geo_rel_system
    ON dim_geo_relationship (system, rel_type);
"""

CREATE_GEO_CODE = """\
CREATE TABLE IF NOT EXISTS dim_geo_code (
    geo_id  TEXT NOT NULL REFERENCES dim_geo_entity(geo_id),
    system  TEXT NOT NULL,
    code    TEXT NOT NULL,
    PRIMARY KEY (geo_id, system)
);
CREATE INDEX IF NOT EXISTS idx_dim_geo_code_lookup
    ON dim_geo_code (system, code);
"""

# Execute in this order to satisfy FK dependencies.
CREATE_ALL_GEO_TABLES = (
    CREATE_GEO_ENTITY
    + CREATE_GEO_RELATIONSHIP
    + CREATE_GEO_CODE
)
