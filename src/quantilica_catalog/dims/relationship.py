"""Geographic relationship dimension schema and registry helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import polars as pl
from quantilica_io.schema import DataContract, Field

from ..enums import GeoSystem, RelType

GEO_RELATIONSHIP_CONTRACT = DataContract(
    dataset_id="catalog-dim-geo-relationship",
    fields=[
        Field(name="from_geo_id", dtype=pl.Utf8),
        Field(name="to_geo_id", dtype=pl.Utf8),
        Field(name="rel_type", dtype=pl.Utf8),
        Field(name="system", dtype=pl.Utf8),
        Field(name="valid_from", dtype=pl.Date, required=False),
        Field(name="valid_to", dtype=pl.Date, required=False),
    ],
)


@dataclass(frozen=True)
class GeoRelationshipEntry:
    """A single geographic relationship entry."""

    from_geo_id: str
    to_geo_id: str
    rel_type: RelType
    system: GeoSystem
    valid_from: date | None = None
    valid_to: date | None = None

    def to_dict(self) -> dict:
        return {
            "from_geo_id": self.from_geo_id,
            "to_geo_id": self.to_geo_id,
            "rel_type": self.rel_type.value,
            "system": self.system.value,
            "valid_from": self.valid_from,
            "valid_to": self.valid_to,
        }


def geo_relationship_entries_to_frame(
    entries: list[GeoRelationshipEntry],
) -> pl.DataFrame:
    """Convert a list of GeoRelationshipEntry objects to a validated DataFrame."""
    schema = {f.name: f.dtype for f in GEO_RELATIONSHIP_CONTRACT.fields}
    if not entries:
        return pl.DataFrame(schema=schema)
    df = pl.DataFrame([e.to_dict() for e in entries])
    df = GEO_RELATIONSHIP_CONTRACT.cast(df)
    GEO_RELATIONSHIP_CONTRACT.validate(df)
    return df


def relationships_at(
    df: pl.DataFrame, reference_date: date
) -> pl.DataFrame:
    """Filter a relationships DataFrame to those active at reference_date.

    A row is included when:
    - valid_from is null or valid_from <= reference_date
    - valid_to   is null or valid_to   >  reference_date

    Rows with both dates null are timeless and always included.
    """
    ref = pl.lit(reference_date)
    return df.filter(
        (pl.col("valid_from").is_null() | (pl.col("valid_from") <= ref))
        & (pl.col("valid_to").is_null() | (pl.col("valid_to") > ref))
    )
