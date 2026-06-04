"""Adapter: Tesouro Direto price/yield data → canonical fact_observation."""

from __future__ import annotations

import polars as pl

from ..facts.observation import OBSERVATION_CONTRACT

# Metrics from Column enum in tesouro_direto_fetcher.constants (prices dataset)
_PRICE_YIELD_COLS = [
    "buy_yield",
    "sell_yield",
    "buy_price",
    "sell_price",
    "base_price",
]


def to_observations(df: pl.DataFrame) -> pl.DataFrame:
    """Convert a Tesouro Direto prices DataFrame to the canonical format.

    Each (reference_date, bond_type, maturity_date, metric) combination
    becomes one observation row. The indicator_id encodes bond type,
    maturity date, and metric so that different maturities of the same
    bond type remain distinct indicators.

    Input contract (matches DATASET_PRICES_RATES from tesouro-direto-fetcher):
        reference_date: Date, bond_type: Utf8, maturity_date: Date,
        buy_yield?: Float64, sell_yield?: Float64, buy_price?: Float64,
        sell_price?: Float64, base_price?: Float64
    """
    present = [c for c in _PRICE_YIELD_COLS if c in df.columns]
    result = (
        df.select(
            ["reference_date", "bond_type", "maturity_date", *present]
        )
        .unpivot(
            on=present,
            index=["reference_date", "bond_type", "maturity_date"],
            variable_name="_metric",
            value_name="value",
        )
        .with_columns(
            indicator_id=pl.concat_str(
                pl.lit("td:"),
                pl.col("bond_type"),
                pl.lit(":"),
                pl.col("maturity_date").cast(pl.Utf8),
                pl.lit(":"),
                pl.col("_metric"),
            ),
            geo_id=pl.lit(None).cast(pl.Utf8),
            date_end=pl.lit(None).cast(pl.Date),
        )
        .rename({"reference_date": "date"})
        .select(["indicator_id", "date", "geo_id", "value", "date_end"])
    )
    OBSERVATION_CONTRACT.validate(result)
    return result
