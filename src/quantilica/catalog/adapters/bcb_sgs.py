"""Adapter: BCB-SGS observations → canonical fact_observation."""

from __future__ import annotations

import polars as pl

from ..facts.observation import OBSERVATION_CONTRACT


def to_observations(df: pl.DataFrame) -> pl.DataFrame:
    """Convert a BCB-SGS DataFrame to the canonical observation format.

    Input contract (matches SGS_CONTRACT):
        series_id: Int64, date: Date, value: Float64?, date_end: Date?
    """
    result = (
        df.with_columns(
            indicator_id=pl.concat_str(
                pl.lit("bcb-sgs:"),
                pl.col("series_id").cast(pl.Utf8),
            ),
            geo_id=pl.lit(None).cast(pl.Utf8),
        )
        .select(["indicator_id", "date", "geo_id", "value", "date_end"])
    )
    OBSERVATION_CONTRACT.validate(result)
    return result
