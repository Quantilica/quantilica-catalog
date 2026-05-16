"""Adapter: INMET BDMEP observations → canonical fact_observation."""

from __future__ import annotations

import polars as pl

from ..facts.observation import OBSERVATION_CONTRACT

# Mirrors _MEASURE_COLS from inmet_fetcher.reader — duplicated here so this
# package has no hard dependency on inmet-fetcher at import time.
_MEASURE_COLS = [
    "precipitacao",
    "pressao_atmosferica",
    "pressao_atmosferica_maxima",
    "pressao_atmosferica_minima",
    "radiacao",
    "temperatura_ar",
    "temperatura_orvalho",
    "temperatura_maxima",
    "temperatura_minima",
    "temperatura_orvalho_maxima",
    "temperatura_orvalho_minima",
    "umidade_relativa_maxima",
    "umidade_relativa_minima",
    "umidade_relativa",
    "vento_direcao",
    "vento_rajada",
    "vento_velocidade",
]


def to_observations(df: pl.DataFrame) -> pl.DataFrame:
    """Convert an INMET BDMEP DataFrame to the canonical observation format.

    Each (station, timestamp, measurement) triple becomes one observation
    row. The ``indicator_id`` encodes both the station WMO code and the
    measurement name so that different stations are separate indicators,
    matching the pattern used by BCB-SGS (series_id per indicator).

    Sub-daily timestamp resolution is truncated to day; callers that need
    hourly granularity should work directly with the BDMEP contract.

    Input contract (matches BDMEP_CONTRACT from inmet-fetcher):
        codigo_wmo: Utf8, data_hora: Datetime, *measurement_cols: Float64?
    """
    present = [c for c in _MEASURE_COLS if c in df.columns]
    result = (
        df.select(["codigo_wmo", "data_hora", *present])
        .unpivot(
            on=present,
            index=["codigo_wmo", "data_hora"],
            variable_name="_measure",
            value_name="value",
        )
        .with_columns(
            indicator_id=pl.concat_str(
                pl.lit("inmet:"),
                pl.col("codigo_wmo"),
                pl.lit(":"),
                pl.col("_measure"),
            ),
            geo_id=pl.concat_str(
                pl.lit("INMET:"),
                pl.col("codigo_wmo"),
            ),
            date=pl.col("data_hora").dt.date(),
            date_end=pl.lit(None).cast(pl.Date),
        )
        .select(["indicator_id", "date", "geo_id", "value", "date_end"])
    )
    OBSERVATION_CONTRACT.validate(result)
    return result
