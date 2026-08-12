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
        """Return the entry as a dictionary.

        Returns:
            A dictionary representation of the entry.
        """
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
    """Convert a list of GeoEntityEntry objects to a validated DataFrame.

    Args:
        entries: A list of GeoEntityEntry objects.

    Returns:
        A validated Polars DataFrame matching GEO_ENTITY_CONTRACT.
    """
    schema = {f.name: f.dtype for f in GEO_ENTITY_CONTRACT.fields}
    if not entries:
        return pl.DataFrame(schema=schema)
    df = pl.DataFrame([e.to_dict() for e in entries])
    df = GEO_ENTITY_CONTRACT.cast(df)
    GEO_ENTITY_CONTRACT.validate(df)
    return df


# ── geo_id builders ───────────────────────────────────────────────────────────


def country_id() -> str:
    """Build the geographic ID for the country level.

    Returns:
        The country geographic ID.
    """
    return "BR"


def region_id(ibge_region_code: str) -> str:
    """Build the geographic ID for a region.

    Args:
        ibge_region_code: The IBGE region code.

    Returns:
        The region geographic ID.
    """
    return f"BR:R:{ibge_region_code}"


def state_id(uf: str) -> str:
    """Build the geographic ID for a state.

    Args:
        uf: The state abbreviation (UF).

    Returns:
        The state geographic ID.
    """
    return f"BR:{uf.upper()}"


def mesoregion_id(ibge_code: str) -> str:
    """Build the geographic ID for a mesoregion.

    Args:
        ibge_code: The IBGE mesoregion code.

    Returns:
        The mesoregion geographic ID.
    """
    return f"BR:MR:{ibge_code}"


def microregion_id(ibge_code: str) -> str:
    """Build the geographic ID for a microregion.

    Args:
        ibge_code: The IBGE microregion code.

    Returns:
        The microregion geographic ID.
    """
    return f"BR:MCR:{ibge_code}"


def municipality_id(ibge_mun_code: str) -> str:
    """Build the geographic ID for a municipality.

    Args:
        ibge_mun_code: The IBGE municipality code.

    Returns:
        The municipality geographic ID.
    """
    return f"BR:M:{ibge_mun_code}"


def district_id(ibge_code: str) -> str:
    """Build the geographic ID for a district.

    Args:
        ibge_code: The IBGE district code.

    Returns:
        The district geographic ID.
    """
    return f"BR:D:{ibge_code}"


def subdistrict_id(ibge_code: str) -> str:
    """Build the geographic ID for a subdistrict.

    Args:
        ibge_code: The IBGE subdistrict code.

    Returns:
        The subdistrict geographic ID.
    """
    return f"BR:SD:{ibge_code}"


def census_sector_id(code: str) -> str:
    """Build the geographic ID for a census sector.

    Args:
        code: The census sector code.

    Returns:
        The census sector geographic ID.
    """
    return f"BR:CS:{code}"


def station_id(source: str, code: str) -> str:
    """Build the geographic ID for a weather or monitoring station.

    Args:
        source: The source identifier (e.g., INMET).
        code: The station code.

    Returns:
        The station geographic ID.
    """
    return f"{source.upper()}:{code}"
