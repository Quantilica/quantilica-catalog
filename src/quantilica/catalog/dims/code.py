"""Geographic external-code dimension schema and registry helpers."""

from __future__ import annotations

from dataclasses import dataclass

import polars as pl
from quantilica.analytics.schema import DataContract, Field

GEO_CODE_CONTRACT = DataContract(
    dataset_id="catalog-dim-geo-code",
    fields=[
        Field(name="geo_id", dtype=pl.Utf8),
        Field(name="system", dtype=pl.Utf8),
        Field(name="code", dtype=pl.Utf8),
    ],
)


@dataclass(frozen=True)
class GeoCodeEntry:
    """A single external-code entry for a geographic entity."""

    geo_id: str
    system: str
    code: str

    def to_dict(self) -> dict:
        return {
            "geo_id": self.geo_id,
            "system": self.system,
            "code": self.code,
        }


def geo_code_entries_to_frame(
    entries: list[GeoCodeEntry],
) -> pl.DataFrame:
    """Convert a list of GeoCodeEntry objects to a validated DataFrame."""
    schema = {f.name: f.dtype for f in GEO_CODE_CONTRACT.fields}
    if not entries:
        return pl.DataFrame(schema=schema)
    df = pl.DataFrame([e.to_dict() for e in entries])
    df = GEO_CODE_CONTRACT.cast(df)
    GEO_CODE_CONTRACT.validate(df)
    return df
