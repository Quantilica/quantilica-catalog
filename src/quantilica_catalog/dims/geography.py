"""Geography dimension schema and geo_id builders."""

from __future__ import annotations

import polars as pl
from quantilica_io.schema import DataContract, Field

GEOGRAPHY_CONTRACT = DataContract(
    dataset_id="catalog-dim-geography",
    fields=[
        Field(name="geo_id", dtype=pl.Utf8),
        Field(name="geo_level", dtype=pl.Utf8),
        Field(name="name", dtype=pl.Utf8),
        Field(name="ibge_code", dtype=pl.Utf8, required=False),
        Field(name="uf", dtype=pl.Utf8, required=False),
        Field(name="region", dtype=pl.Utf8, required=False),
        Field(name="parent_geo_id", dtype=pl.Utf8, required=False),
        Field(name="latitude", dtype=pl.Float64, required=False),
        Field(name="longitude", dtype=pl.Float64, required=False),
    ],
)


# Canonical geo_id builders — kept as pure functions so callers do not
# need to duplicate the formatting convention.


def country_id() -> str:
    return "BR"


def region_id(ibge_region_code: str) -> str:
    return f"BR:R:{ibge_region_code}"


def state_id(uf: str) -> str:
    return f"BR:{uf.upper()}"


def municipality_id(ibge_mun_code: str) -> str:
    return f"BR:M:{ibge_mun_code}"


def station_id(source: str, code: str) -> str:
    return f"{source.upper()}:{code}"
