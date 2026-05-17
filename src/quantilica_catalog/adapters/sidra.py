"""Adapter: SIDRA (IBGE Agregados) observations → canonical fact_observation.

Input contract (SIDRA_RESULT_CONTRACT):
    agregado_id:   Utf8     — aggregate ID (e.g. "1705")
    variavel_id:   Utf8     — variable ID (e.g. "93")
    categoria_ids: Utf8?    — pipe-separated category IDs sorted by
                              classification order (e.g. "49223|49702");
                              null when no classifications apply
    geo_id:        Utf8?    — canonical geo_id (e.g. "IBGE:N6:3550308");
                              null for nationally-scoped series
    data_inicio:   Date     — first day of the period
    data_fim:      Date?    — last day of the period; null for standard
                              frequencies (monthly/quarterly/semi-annual/yearly),
                              non-null for rolling-quarterly and multi-year
    frequencia:    Utf8     — period frequency string from sidra_fetcher.periodos
    value:         Float64? — observed value

Raises ValueError for any row with frequencia == 'nao_reconhecida'.
"""

from __future__ import annotations

import polars as pl
from quantilica_io.schema import DataContract, Field

from ..enums import Frequency
from ..facts.observation import OBSERVATION_CONTRACT

SIDRA_RESULT_CONTRACT = DataContract(
    dataset_id="sidra-result",
    fields=[
        Field(name="agregado_id", dtype=pl.Utf8),
        Field(name="variavel_id", dtype=pl.Utf8),
        Field(name="categoria_ids", dtype=pl.Utf8, required=False),
        Field(name="geo_id", dtype=pl.Utf8, required=False),
        Field(name="data_inicio", dtype=pl.Date),
        Field(name="data_fim", dtype=pl.Date, required=False),
        Field(name="frequencia", dtype=pl.Utf8),
        Field(name="value", dtype=pl.Float64, required=False),
    ],
)

SIDRA_FREQUENCIA_TO_FREQUENCY: dict[str, Frequency] = {
    "mensal": Frequency.MONTHLY,
    "trimestral": Frequency.QUARTERLY,
    "trimestre_movel": Frequency.ROLLING_QUARTERLY,
    "semestral": Frequency.SEMI_ANNUAL,
    "anual": Frequency.YEARLY,
    "plurianual": Frequency.MULTI_YEAR,
    "nao_reconhecida": Frequency.IRREGULAR,
}

# Frequencies where date_end must be propagated because date alone is
# insufficient to reconstruct the full interval.
_INTERVAL_FREQUENCIAS = {"trimestre_movel", "plurianual"}


def sidra_frequencia_to_frequency(freq: str) -> Frequency:
    """Map a sidra_fetcher.periodos frequency string to a Frequency enum value."""
    try:
        return SIDRA_FREQUENCIA_TO_FREQUENCY[freq]
    except KeyError:
        return Frequency.IRREGULAR


def to_observations(df: pl.DataFrame) -> pl.DataFrame:
    """Convert a SIDRA result DataFrame to the canonical observation format.

    Input contract: SIDRA_RESULT_CONTRACT.
    Raises ValueError for any row with frequencia == 'nao_reconhecida'.
    """
    bad = (df["frequencia"] == "nao_reconhecida").sum()
    if bad > 0:
        raise ValueError(
            f"{bad} row(s) have frequencia='nao_reconhecida' and cannot be "
            "mapped to a date. Filter or correct these rows before calling "
            "to_observations()."
        )

    result = (
        df.with_columns(
            indicator_id=pl.when(pl.col("categoria_ids").is_null())
            .then(
                pl.concat_str(
                    pl.lit("sidra:"),
                    pl.col("agregado_id"),
                    pl.lit(":"),
                    pl.col("variavel_id"),
                )
            )
            .otherwise(
                pl.concat_str(
                    pl.lit("sidra:"),
                    pl.col("agregado_id"),
                    pl.lit(":"),
                    pl.col("variavel_id"),
                    pl.lit(":"),
                    pl.col("categoria_ids"),
                )
            ),
            date=pl.col("data_inicio"),
            date_end=pl.when(
                pl.col("frequencia").is_in(list(_INTERVAL_FREQUENCIAS))
            )
            .then(pl.col("data_fim"))
            .otherwise(pl.lit(None).cast(pl.Date)),
        )
        .select(["indicator_id", "date", "geo_id", "value", "date_end"])
    )
    OBSERVATION_CONTRACT.validate(result)
    return result
