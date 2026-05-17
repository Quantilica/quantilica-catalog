"""Indicator dimension schema and registry helpers."""

from __future__ import annotations

from dataclasses import dataclass

import polars as pl
from quantilica_io.schema import DataContract, Field

from ..enums import DataCategory, Frequency

INDICATOR_CONTRACT = DataContract(
    dataset_id="catalog-dim-indicator",
    fields=[
        Field(name="indicator_id", dtype=pl.Utf8),
        Field(name="source_id", dtype=pl.Utf8),
        Field(name="source_dataset_id", dtype=pl.Utf8),
        Field(name="name", dtype=pl.Utf8),
        Field(name="category", dtype=pl.Utf8),
        Field(name="subcategory", dtype=pl.Utf8, required=False),
        Field(name="unit", dtype=pl.Utf8, required=False),
        Field(name="frequency", dtype=pl.Utf8, required=False),
        Field(name="geo_level", dtype=pl.Utf8, required=False),
        Field(name="description", dtype=pl.Utf8, required=False),
    ],
)


@dataclass(frozen=True)
class IndicatorEntry:
    """A single indicator registry entry."""

    indicator_id: str
    source_id: str
    source_dataset_id: str
    name: str
    category: DataCategory
    subcategory: str | None = None
    unit: str | None = None
    frequency: Frequency | None = None
    geo_level: str | None = None
    description: str | None = None

    def to_dict(self) -> dict:
        return {
            "indicator_id": self.indicator_id,
            "source_id": self.source_id,
            "source_dataset_id": self.source_dataset_id,
            "name": self.name,
            "category": self.category.value,
            "subcategory": self.subcategory,
            "unit": self.unit,
            "frequency": (
                self.frequency.value if self.frequency else None
            ),
            "geo_level": self.geo_level,
            "description": self.description,
        }


def entries_to_frame(entries: list[IndicatorEntry]) -> pl.DataFrame:
    """Convert a list of IndicatorEntry objects to a validated DataFrame."""
    schema = {f.name: f.dtype for f in INDICATOR_CONTRACT.fields}
    if not entries:
        return pl.DataFrame(schema=schema)
    df = pl.DataFrame([e.to_dict() for e in entries])
    df = INDICATOR_CONTRACT.cast(df)
    INDICATOR_CONTRACT.validate(df)
    return df
