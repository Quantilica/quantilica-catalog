"""Observation fact schema — the core of the unified catalog.

Every row in ``fact_observation`` answers: *what was the value of indicator X
at time T in place G?*

``geo_id`` is null for nationally-scoped series (BCB-SGS, RTN, Tesouro
Direto) that have no geographic disaggregation.

``date_end`` is non-null only for interval observations where the source
reports a range rather than a point in time (e.g. BCB-SGS daily ranges).
"""

from __future__ import annotations

import polars as pl
from quantilica_io.schema import DataContract, Field

OBSERVATION_CONTRACT = DataContract(
    dataset_id="catalog-fact-observation",
    fields=[
        Field(name="indicator_id", dtype=pl.Utf8),
        Field(name="date", dtype=pl.Date),
        Field(
            name="geo_id",
            dtype=pl.Utf8,
            required=False,
        ),
        Field(
            name="value",
            dtype=pl.Float64,
            required=False,
        ),
        Field(
            name="date_end",
            dtype=pl.Date,
            required=False,
        ),
    ],
)
