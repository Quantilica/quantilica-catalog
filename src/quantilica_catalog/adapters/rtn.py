"""Adapter: RTN (Relatório do Tesouro Nacional) → canonical fact_observation."""

from __future__ import annotations

import polars as pl

from ..facts.observation import OBSERVATION_CONTRACT

_YEAR = "year"
_MONTH = "month"
_QUARTER = "quarter"
_ACCOUNT = "account"
_VALUE = "value"


def to_observations(
    df: pl.DataFrame,
    sheet_name: str,
    period: str,
) -> pl.DataFrame:
    """Convert an RTN sheet DataFrame to the canonical observation format.

    ``period`` must be one of ``"monthly"``, ``"quarterly"``, or
    ``"yearly"``.  The date is normalised to the first calendar day of
    each period (e.g. 2024-Q2 → 2024-04-01).

    Input contract (matches ``build_contract`` from rtn-fetcher):
        year: Int64, month?: Int64, quarter?: Int64,
        account: Utf8, value: Float64?
    """
    result = (
        df.with_columns(
            indicator_id=pl.concat_str(
                pl.lit(f"rtn:{sheet_name}:"),
                pl.col(_ACCOUNT),
            ),
            date=_date_expr(period),
            geo_id=pl.lit(None).cast(pl.Utf8),
            date_end=pl.lit(None).cast(pl.Date),
        )
        .rename({_VALUE: "value"})
        .select(["indicator_id", "date", "geo_id", "value", "date_end"])
    )
    OBSERVATION_CONTRACT.validate(result)
    return result


def _date_expr(period: str) -> pl.Expr:
    year = pl.col(_YEAR).cast(pl.Utf8).str.zfill(4)
    if period == "monthly":
        month = pl.col(_MONTH).cast(pl.Utf8).str.zfill(2)
        return pl.concat_str(year, pl.lit("-"), month, pl.lit("-01")).str.to_date()
    if period == "quarterly":
        # Q1→01, Q2→04, Q3→07, Q4→10
        month = ((pl.col(_QUARTER) - 1) * 3 + 1).cast(pl.Utf8).str.zfill(2)
        return pl.concat_str(year, pl.lit("-"), month, pl.lit("-01")).str.to_date()
    # yearly
    return pl.concat_str(year, pl.lit("-01-01")).str.to_date()
