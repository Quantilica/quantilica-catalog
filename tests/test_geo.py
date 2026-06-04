"""Tests for the geographic dimension contracts, dataclasses, and builders."""

from datetime import date

import polars as pl
import pytest

from quantilica.catalog import (
    GEO_CODE_CONTRACT,
    GEO_ENTITY_CONTRACT,
    GEO_RELATIONSHIP_CONTRACT,
    GeoCodeEntry,
    GeoEntityEntry,
    GeoRelationshipEntry,
    GeoSystem,
    GeoType,
    RelType,
    census_sector_id,
    country_id,
    district_id,
    geo_code_entries_to_frame,
    geo_entity_entries_to_frame,
    geo_relationship_entries_to_frame,
    mesoregion_id,
    microregion_id,
    municipality_id,
    region_id,
    relationships_at,
    state_id,
    station_id,
    subdistrict_id,
)
from quantilica.catalog.sql.ddl import (
    CREATE_ALL_GEO_TABLES,
    CREATE_GEO_CODE,
    CREATE_GEO_ENTITY,
    CREATE_GEO_RELATIONSHIP,
)


# ── GEO_ENTITY_CONTRACT ───────────────────────────────────────────────────────


def test_geo_entity_contract_valid():
    df = pl.DataFrame(
        {
            "geo_id": ["BR:SP"],
            "geo_type": ["territory"],
            "name": ["São Paulo"],
            "latitude": [None],
            "longitude": [None],
        },
        schema={
            "geo_id": pl.Utf8,
            "geo_type": pl.Utf8,
            "name": pl.Utf8,
            "latitude": pl.Float64,
            "longitude": pl.Float64,
        },
    )
    GEO_ENTITY_CONTRACT.validate(df)


def test_geo_entity_contract_missing_required():
    df = pl.DataFrame({"geo_id": ["BR"]})
    with pytest.raises(ValueError, match="geo_type"):
        GEO_ENTITY_CONTRACT.validate(df)


def test_geo_entity_contract_wrong_type():
    df = pl.DataFrame(
        {
            "geo_id": ["INMET:A701"],
            "geo_type": ["station"],
            "name": ["Estação A701"],
            "latitude": ["not-a-float"],
            "longitude": [None],
        },
        schema={
            "geo_id": pl.Utf8,
            "geo_type": pl.Utf8,
            "name": pl.Utf8,
            "latitude": pl.Utf8,
            "longitude": pl.Utf8,
        },
    )
    with pytest.raises(TypeError):
        GEO_ENTITY_CONTRACT.validate(df)


# ── GEO_RELATIONSHIP_CONTRACT ─────────────────────────────────────────────────


def test_geo_relationship_contract_valid():
    df = pl.DataFrame(
        {
            "from_geo_id": ["BR:M:3550308"],
            "to_geo_id": ["BR:SP"],
            "rel_type": ["administrative_parent"],
            "system": ["ibge_traditional"],
            "valid_from": [None],
            "valid_to": [None],
        },
        schema={
            "from_geo_id": pl.Utf8,
            "to_geo_id": pl.Utf8,
            "rel_type": pl.Utf8,
            "system": pl.Utf8,
            "valid_from": pl.Date,
            "valid_to": pl.Date,
        },
    )
    GEO_RELATIONSHIP_CONTRACT.validate(df)


def test_geo_relationship_contract_missing_required():
    df = pl.DataFrame({"from_geo_id": ["BR:SP"], "to_geo_id": ["BR:R:3"]})
    with pytest.raises(ValueError, match="rel_type"):
        GEO_RELATIONSHIP_CONTRACT.validate(df)


# ── GEO_CODE_CONTRACT ─────────────────────────────────────────────────────────


def test_geo_code_contract_valid():
    df = pl.DataFrame(
        {
            "geo_id": ["BR:M:3550308"],
            "system": ["ibge"],
            "code": ["3550308"],
        },
        schema={
            "geo_id": pl.Utf8,
            "system": pl.Utf8,
            "code": pl.Utf8,
        },
    )
    GEO_CODE_CONTRACT.validate(df)


# ── Dataclass roundtrips ──────────────────────────────────────────────────────


def test_geo_entity_entries_to_frame_roundtrip():
    entry = GeoEntityEntry(
        geo_id="BR:SP",
        geo_type=GeoType.TERRITORY,
        name="São Paulo",
    )
    df = geo_entity_entries_to_frame([entry])
    assert df.shape == (1, 6)
    assert df["geo_id"][0] == "BR:SP"
    assert df["geo_type"][0] == "territory"
    assert df["latitude"].is_null().all()


def test_geo_entity_entries_to_frame_empty():
    df = geo_entity_entries_to_frame([])
    assert df.shape[0] == 0
    assert "geo_id" in df.columns


def test_geo_entity_entry_station():
    entry = GeoEntityEntry(
        geo_id="INMET:A701",
        geo_type=GeoType.STATION,
        name="Estação A701",
        latitude=-23.5,
        longitude=-46.6,
    )
    df = geo_entity_entries_to_frame([entry])
    assert df["latitude"][0] == pytest.approx(-23.5)
    assert df["geo_type"][0] == "station"


def test_geo_relationship_entries_to_frame_roundtrip():
    entry = GeoRelationshipEntry(
        from_geo_id="BR:M:3550308",
        to_geo_id="BR:SP",
        rel_type=RelType.ADMINISTRATIVE_PARENT,
        system=GeoSystem.IBGE_TRADITIONAL,
    )
    df = geo_relationship_entries_to_frame([entry])
    assert df["rel_type"][0] == "administrative_parent"
    assert df["system"][0] == "ibge_traditional"


def test_geo_relationship_valid_from():
    entry = GeoRelationshipEntry(
        from_geo_id="BR:M:3550308",
        to_geo_id="BR:RegInt:35001",
        rel_type=RelType.ADMINISTRATIVE_PARENT,
        system=GeoSystem.IBGE_RGINT,
        valid_from=date(2017, 1, 1),
    )
    df = geo_relationship_entries_to_frame([entry])
    assert df["valid_from"][0] == date(2017, 1, 1)


def test_geo_code_entries_to_frame_roundtrip():
    entry = GeoCodeEntry(geo_id="BR:M:3550308", system="ibge", code="3550308")
    df = geo_code_entries_to_frame([entry])
    assert df["code"][0] == "3550308"


# ── geo_id builders ───────────────────────────────────────────────────────────


def test_builders():
    assert country_id() == "BR"
    assert region_id("3") == "BR:R:3"
    assert state_id("sp") == "BR:SP"
    assert state_id("SP") == "BR:SP"
    assert mesoregion_id("3501") == "BR:MR:3501"
    assert microregion_id("35001") == "BR:MCR:35001"
    assert municipality_id("3550308") == "BR:M:3550308"
    assert district_id("355030805") == "BR:D:355030805"
    assert subdistrict_id("35503080501") == "BR:SD:35503080501"
    assert census_sector_id("355030805000001") == "BR:CS:355030805000001"
    assert station_id("INMET", "A701") == "INMET:A701"
    assert station_id("inmet", "a701") == "INMET:a701"


# ── DDL ───────────────────────────────────────────────────────────────────────


def test_ddl_constants_non_empty():
    assert "dim_geo_entity" in CREATE_GEO_ENTITY
    assert "dim_geo_relationship" in CREATE_GEO_RELATIONSHIP
    assert "dim_geo_code" in CREATE_GEO_CODE


def test_create_all_geo_tables_order():
    # dim_geo_entity must be defined before the FK-dependent tables
    entity_pos = CREATE_ALL_GEO_TABLES.index("dim_geo_entity")
    rel_pos = CREATE_ALL_GEO_TABLES.index("dim_geo_relationship")
    code_pos = CREATE_ALL_GEO_TABLES.index("dim_geo_code")
    assert entity_pos < rel_pos < code_pos


def test_ddl_geometry_column():
    assert "geometry" in CREATE_GEO_ENTITY
    assert "BYTEA" in CREATE_GEO_ENTITY


# ── Geometry field ────────────────────────────────────────────────────────────

# Minimal WKB for a point (little-endian, WGS84 not encoded — just valid bytes)
_DUMMY_WKB = bytes.fromhex("0101000000000000000000f03f0000000000000040")


def test_geo_entity_geometry_roundtrip():
    entry = GeoEntityEntry(
        geo_id="BR:SP",
        geo_type=GeoType.TERRITORY,
        name="São Paulo",
        geometry=_DUMMY_WKB,
    )
    df = geo_entity_entries_to_frame([entry])
    assert df["geometry"][0] == _DUMMY_WKB


def test_geo_entity_geometry_optional():
    entry = GeoEntityEntry(
        geo_id="BR:M:3550308",
        geo_type=GeoType.TERRITORY,
        name="São Paulo (município)",
    )
    df = geo_entity_entries_to_frame([entry])
    assert df["geometry"].is_null().all()


def test_geo_entity_contract_geometry_wrong_type():
    df = pl.DataFrame(
        {
            "geo_id": ["BR"],
            "geo_type": ["territory"],
            "name": ["Brasil"],
            "latitude": [None],
            "longitude": [None],
            "geometry": ["not-bytes"],
        },
        schema={
            "geo_id": pl.Utf8,
            "geo_type": pl.Utf8,
            "name": pl.Utf8,
            "latitude": pl.Float64,
            "longitude": pl.Float64,
            "geometry": pl.Utf8,
        },
    )
    with pytest.raises(TypeError):
        GEO_ENTITY_CONTRACT.validate(df)


# ── relationships_at ──────────────────────────────────────────────────────────


def _make_rel_df(rows: list[dict]) -> pl.DataFrame:
    schema = {f.name: f.dtype for f in GEO_RELATIONSHIP_CONTRACT.fields}
    return pl.DataFrame(rows, schema=schema)


def test_relationships_at_timeless():
    df = _make_rel_df([{
        "from_geo_id": "BR:M:1",
        "to_geo_id": "BR:SP",
        "rel_type": "administrative_parent",
        "system": "ibge_traditional",
        "valid_from": None,
        "valid_to": None,
    }])
    result = relationships_at(df, date(2020, 1, 1))
    assert len(result) == 1


def test_relationships_at_within_range():
    df = _make_rel_df([{
        "from_geo_id": "BR:M:1",
        "to_geo_id": "BR:MR:old",
        "rel_type": "administrative_parent",
        "system": "ibge_traditional",
        "valid_from": date(2010, 1, 1),
        "valid_to": date(2022, 1, 1),
    }])
    assert len(relationships_at(df, date(2015, 6, 1))) == 1


def test_relationships_at_before_valid_from():
    df = _make_rel_df([{
        "from_geo_id": "BR:M:1",
        "to_geo_id": "BR:MR:new",
        "rel_type": "administrative_parent",
        "system": "ibge_traditional",
        "valid_from": date(2022, 1, 1),
        "valid_to": None,
    }])
    assert len(relationships_at(df, date(2020, 1, 1))) == 0


def test_relationships_at_after_valid_to():
    df = _make_rel_df([{
        "from_geo_id": "BR:M:1",
        "to_geo_id": "BR:MR:old",
        "rel_type": "administrative_parent",
        "system": "ibge_traditional",
        "valid_from": None,
        "valid_to": date(2022, 1, 1),
    }])
    assert len(relationships_at(df, date(2022, 1, 1))) == 0


def test_relationships_at_on_valid_from_boundary():
    df = _make_rel_df([{
        "from_geo_id": "BR:M:1",
        "to_geo_id": "BR:MR:new",
        "rel_type": "administrative_parent",
        "system": "ibge_traditional",
        "valid_from": date(2022, 1, 1),
        "valid_to": None,
    }])
    assert len(relationships_at(df, date(2022, 1, 1))) == 1


def test_relationships_at_selects_correct_version():
    """Two versions of the same relation; only one is active at reference_date."""
    df = _make_rel_df([
        {
            "from_geo_id": "BR:M:1",
            "to_geo_id": "BR:MR:old",
            "rel_type": "administrative_parent",
            "system": "ibge_traditional",
            "valid_from": None,
            "valid_to": date(2022, 1, 1),
        },
        {
            "from_geo_id": "BR:M:1",
            "to_geo_id": "BR:MR:new",
            "rel_type": "administrative_parent",
            "system": "ibge_traditional",
            "valid_from": date(2022, 1, 1),
            "valid_to": None,
        },
    ])
    result_old = relationships_at(df, date(2021, 12, 31))
    result_new = relationships_at(df, date(2022, 6, 1))
    assert result_old["to_geo_id"][0] == "BR:MR:old"
    assert result_new["to_geo_id"][0] == "BR:MR:new"
