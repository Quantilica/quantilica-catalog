"""Tests for the SIDRA adapter."""

from datetime import date

import polars as pl
import pytest

from quantilica.catalog.adapters.sidra import (
    SIDRA_FREQUENCIA_TO_FREQUENCY,
    sidra_frequencia_to_frequency,
    to_observations,
)
from quantilica.catalog.enums import Frequency


# ── helpers ──────────────────────────────────────────────────────────────────


def _make_df(**overrides) -> pl.DataFrame:
    """Return a minimal valid SIDRA result row."""
    defaults = {
        "agregado_id": ["1705"],
        "variavel_id": ["93"],
        "categoria_ids": [None],
        "geo_id": [None],
        "data_inicio": [date(2023, 1, 1)],
        "data_fim": [None],
        "frequencia": ["anual"],
        "value": [100.0],
    }
    defaults.update(overrides)
    return pl.DataFrame(
        defaults,
        schema={
            "agregado_id": pl.Utf8,
            "variavel_id": pl.Utf8,
            "categoria_ids": pl.Utf8,
            "geo_id": pl.Utf8,
            "data_inicio": pl.Date,
            "data_fim": pl.Date,
            "frequencia": pl.Utf8,
            "value": pl.Float64,
        },
    )


# ── indicator_id ──────────────────────────────────────────────────────────────


def test_indicator_id_no_categories():
    out = to_observations(_make_df())
    assert out["indicator_id"][0] == "sidra:1705:93"


def test_indicator_id_one_category():
    df = _make_df(categoria_ids=["49223"])
    out = to_observations(df)
    assert out["indicator_id"][0] == "sidra:1705:93:49223"


def test_indicator_id_two_categories():
    df = _make_df(categoria_ids=["49223|49702"])
    out = to_observations(df)
    assert out["indicator_id"][0] == "sidra:1705:93:49223|49702"


# ── date_end by frequency ─────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "frequencia",
    ["mensal", "trimestral", "semestral", "anual"],
)
def test_date_end_null_for_standard_frequencies(frequencia):
    df = _make_df(frequencia=[frequencia], data_fim=[date(2023, 12, 31)])
    out = to_observations(df)
    assert out["date_end"][0] is None


def test_date_end_populated_for_trimestre_movel():
    df = _make_df(
        frequencia=["trimestre_movel"],
        data_inicio=[date(2023, 1, 1)],
        data_fim=[date(2023, 3, 31)],
    )
    out = to_observations(df)
    assert out["date_end"][0] == date(2023, 3, 31)


def test_date_end_populated_for_plurianual():
    # Censo Decenal: 2010–2022
    df = _make_df(
        frequencia=["plurianual"],
        data_inicio=[date(2010, 1, 1)],
        data_fim=[date(2022, 12, 31)],
    )
    out = to_observations(df)
    assert out["date_end"][0] == date(2022, 12, 31)


def test_date_populated_from_data_inicio():
    df = _make_df(data_inicio=[date(2022, 7, 1)], frequencia=["semestral"])
    out = to_observations(df)
    assert out["date"][0] == date(2022, 7, 1)


# ── geo_id ────────────────────────────────────────────────────────────────────


def test_geo_id_null_for_national_series():
    out = to_observations(_make_df(geo_id=[None]))
    assert out["geo_id"][0] is None


def test_geo_id_preserved_for_municipality():
    df = _make_df(geo_id=["IBGE:N6:3550308"])
    out = to_observations(df)
    assert out["geo_id"][0] == "IBGE:N6:3550308"


# ── value ─────────────────────────────────────────────────────────────────────


def test_value_preserved():
    df = _make_df(value=[42.5])
    out = to_observations(df)
    assert out["value"][0] == pytest.approx(42.5)


def test_value_null_allowed():
    df = _make_df(value=[None])
    out = to_observations(df)
    assert out["value"][0] is None


# ── output columns ────────────────────────────────────────────────────────────


def test_output_columns():
    out = to_observations(_make_df())
    assert set(out.columns) == {
        "indicator_id", "date", "geo_id", "value", "date_end"
    }


# ── rejection of nao_reconhecida ─────────────────────────────────────────────


def test_rejects_nao_reconhecida():
    df = _make_df(
        frequencia=["nao_reconhecida"],
        data_inicio=[None],
        data_fim=[None],
    )
    with pytest.raises(ValueError, match="nao_reconhecida"):
        to_observations(df)


def test_rejects_nao_reconhecida_reports_count():
    df = pl.concat([
        _make_df(frequencia=["nao_reconhecida"], data_inicio=[None], data_fim=[None]),
        _make_df(frequencia=["nao_reconhecida"], data_inicio=[None], data_fim=[None]),
        _make_df(),
    ])
    with pytest.raises(ValueError, match="2 row"):
        to_observations(df)


# ── frequency mapper ──────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "sidra_freq,expected",
    [
        ("mensal", Frequency.MONTHLY),
        ("trimestral", Frequency.QUARTERLY),
        ("trimestre_movel", Frequency.ROLLING_QUARTERLY),
        ("semestral", Frequency.SEMI_ANNUAL),
        ("anual", Frequency.YEARLY),
        ("plurianual", Frequency.MULTI_YEAR),
        ("nao_reconhecida", Frequency.IRREGULAR),
    ],
)
def test_sidra_frequencia_to_frequency(sidra_freq, expected):
    assert sidra_frequencia_to_frequency(sidra_freq) == expected


def test_sidra_frequencia_to_frequency_unknown_falls_back():
    assert sidra_frequencia_to_frequency("unknown_value") == Frequency.IRREGULAR


def test_sidra_frequencia_map_covers_all_known_values():
    known = {
        "mensal", "trimestral", "trimestre_movel", "semestral",
        "anual", "plurianual", "nao_reconhecida",
    }
    assert set(SIDRA_FREQUENCIA_TO_FREQUENCY.keys()) == known


# ── new Frequency enum values ─────────────────────────────────────────────────


def test_frequency_enum_new_values():
    assert Frequency.SEMI_ANNUAL.value == "semi_annual"
    assert Frequency.ROLLING_QUARTERLY.value == "rolling_quarterly"
    assert Frequency.MULTI_YEAR.value == "multi_year"
