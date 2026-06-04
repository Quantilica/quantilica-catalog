"""Geographic entity dimension schema, registry helpers, and geo_id builders."""

from __future__ import annotations

from dataclasses import dataclass

import polars as pl
from quantilica.analytics.schema import DataContract, Field

from ..enums import GeoType

GEO_ENTITY_CONTRACT = DataContract(
    dataset_id="catalog-dim-geo-entity",
    fields=[
        Field(name="geo_id", dtype=pl.Utf8),
        Field(name="geo_type", dtype=pl.Utf8),
        Field(name="name", dtype=pl.Utf8),
        Field(name="latitude", dtype=pl.Float64, required=False),
        Field(name="longitude", dtype=pl.Float64, required=False),
        Field(name="geometry", dtype=pl.Binary, required=False),
    ],
)


@dataclass(frozen=True)
class GeoEntityEntry:
    """A single geographic entity registry entry."""

    geo_id: str
    geo_type: GeoType
    name: str
    latitude: float | None = None
    longitude: float | None = None
    geometry: bytes | None = None

    def to_dict(self) -> dict:
        return {
            "geo_id": self.geo_id,
            "geo_type": self.geo_type.value,
            "name": self.name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "geometry": self.geometry,
        }


def geo_entity_entries_to_frame(
    entries: list[GeoEntityEntry],
) -> pl.DataFrame:
    """Convert a list of GeoEntityEntry objects to a validated DataFrame."""
    schema = {f.name: f.dtype for f in GEO_ENTITY_CONTRACT.fields}
    if not entries:
        return pl.DataFrame(schema=schema)
    df = pl.DataFrame([e.to_dict() for e in entries])
    df = GEO_ENTITY_CONTRACT.cast(df)
    GEO_ENTITY_CONTRACT.validate(df)
    return df


# ── geo_id builders ───────────────────────────────────────────────────────────


def country_id() -> str:
    return "BR"


def region_id(ibge_region_code: str) -> str:
    return f"BR:R:{ibge_region_code}"


def state_id(uf: str) -> str:
    return f"BR:{uf.upper()}"


def mesoregion_id(ibge_code: str) -> str:
    return f"BR:MR:{ibge_code}"


def microregion_id(ibge_code: str) -> str:
    return f"BR:MCR:{ibge_code}"


def municipality_id(ibge_mun_code: str) -> str:
    return f"BR:M:{ibge_mun_code}"


def district_id(ibge_code: str) -> str:
    return f"BR:D:{ibge_code}"


def subdistrict_id(ibge_code: str) -> str:
    return f"BR:SD:{ibge_code}"


def census_sector_id(code: str) -> str:
    return f"BR:CS:{code}"


def station_id(source: str, code: str) -> str:
    return f"{source.upper()}:{code}"
