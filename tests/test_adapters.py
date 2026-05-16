"""Tests for per-source adapters."""

from datetime import date, datetime

import polars as pl
import pytest

from quantilica_catalog.adapters import bcb_sgs, inmet, rtn, tesouro_direto


# ── BCB-SGS ──────────────────────────────────────────────────────────────────


def test_bcb_sgs_indicator_id():
    df = pl.DataFrame(
        {
            "series_id": [11, 432],
            "date": [date(2025, 1, 1), date(2025, 1, 2)],
            "value": [10.5, 11.0],
            "date_end": [None, None],
        },
        schema={
            "series_id": pl.Int64,
            "date": pl.Date,
            "value": pl.Float64,
            "date_end": pl.Date,
        },
    )
    out = bcb_sgs.to_observations(df)
    assert out["indicator_id"].to_list() == ["bcb-sgs:11", "bcb-sgs:432"]
    assert out["geo_id"].is_null().all()
    assert set(out.columns) == {
        "indicator_id", "date", "geo_id", "value", "date_end"
    }


def test_bcb_sgs_date_end_preserved():
    df = pl.DataFrame(
        {
            "series_id": [11],
            "date": [date(2025, 1, 1)],
            "value": [5.0],
            "date_end": [date(2025, 1, 7)],
        },
        schema={
            "series_id": pl.Int64,
            "date": pl.Date,
            "value": pl.Float64,
            "date_end": pl.Date,
        },
    )
    out = bcb_sgs.to_observations(df)
    assert out["date_end"][0] == date(2025, 1, 7)


# ── RTN ──────────────────────────────────────────────────────────────────────


def test_rtn_monthly_date():
    df = pl.DataFrame(
        {
            "year": [2024],
            "month": [3],
            "account": ["Receita Total"],
            "value": [1_000_000.0],
        },
        schema={
            "year": pl.Int64,
            "month": pl.Int64,
            "account": pl.Utf8,
            "value": pl.Float64,
        },
    )
    out = rtn.to_observations(df, sheet_name="1.1", period="monthly")
    assert out["indicator_id"][0] == "rtn:1.1:Receita Total"
    assert out["date"][0] == date(2024, 3, 1)
    assert out["geo_id"].is_null().all()


@pytest.mark.parametrize(
    "quarter,expected_month",
    [(1, 1), (2, 4), (3, 7), (4, 10)],
)
def test_rtn_quarterly_date(quarter, expected_month):
    df = pl.DataFrame(
        {
            "year": [2024],
            "quarter": [quarter],
            "account": ["Despesa Total"],
            "value": [500_000.0],
        },
        schema={
            "year": pl.Int64,
            "quarter": pl.Int64,
            "account": pl.Utf8,
            "value": pl.Float64,
        },
    )
    out = rtn.to_observations(df, sheet_name="4.1", period="quarterly")
    assert out["date"][0] == date(2024, expected_month, 1)


def test_rtn_yearly_date():
    df = pl.DataFrame(
        {
            "year": [2023],
            "account": ["PIB"],
            "value": [9_000_000.0],
        },
        schema={
            "year": pl.Int64,
            "account": pl.Utf8,
            "value": pl.Float64,
        },
    )
    out = rtn.to_observations(df, sheet_name="2.1", period="yearly")
    assert out["date"][0] == date(2023, 1, 1)


# ── INMET ─────────────────────────────────────────────────────────────────────


def test_inmet_unpivot_row_count():
    df = pl.DataFrame(
        {
            "codigo_wmo": ["A701"],
            "data_hora": [datetime(2025, 1, 1, 12, 0)],
            "temperatura_ar": [25.0],
            "precipitacao": [0.0],
            "vento_velocidade": [3.5],
        },
        schema={
            "codigo_wmo": pl.Utf8,
            "data_hora": pl.Datetime,
            "temperatura_ar": pl.Float64,
            "precipitacao": pl.Float64,
            "vento_velocidade": pl.Float64,
        },
    )
    out = inmet.to_observations(df)
    # 3 measurements × 1 station-hour = 3 rows
    assert len(out) == 3


def test_inmet_indicator_and_geo_ids():
    df = pl.DataFrame(
        {
            "codigo_wmo": ["A701"],
            "data_hora": [datetime(2025, 1, 1, 12, 0)],
            "temperatura_ar": [25.0],
        },
        schema={
            "codigo_wmo": pl.Utf8,
            "data_hora": pl.Datetime,
            "temperatura_ar": pl.Float64,
        },
    )
    out = inmet.to_observations(df)
    assert out["indicator_id"][0] == "inmet:A701:temperatura_ar"
    assert out["geo_id"][0] == "INMET:A701"
    assert out["date"][0] == date(2025, 1, 1)


# ── Tesouro Direto ────────────────────────────────────────────────────────────


def test_tesouro_direto_unpivot_row_count():
    df = pl.DataFrame(
        {
            "reference_date": [date(2025, 1, 2)],
            "bond_type": ["Tesouro Selic"],
            "maturity_date": [date(2029, 3, 1)],
            "buy_price": [14_500.0],
            "sell_price": [14_550.0],
            "buy_yield": [0.12],
            "sell_yield": [0.119],
            "base_price": [None],
        },
        schema={
            "reference_date": pl.Date,
            "bond_type": pl.Utf8,
            "maturity_date": pl.Date,
            "buy_price": pl.Float64,
            "sell_price": pl.Float64,
            "buy_yield": pl.Float64,
            "sell_yield": pl.Float64,
            "base_price": pl.Float64,
        },
    )
    out = tesouro_direto.to_observations(df)
    # 5 metrics × 1 bond = 5 rows
    assert len(out) == 5
    assert out["geo_id"].is_null().all()


def test_tesouro_direto_indicator_id_format():
    df = pl.DataFrame(
        {
            "reference_date": [date(2025, 1, 2)],
            "bond_type": ["Tesouro IPCA+"],
            "maturity_date": [date(2035, 5, 15)],
            "buy_price": [4_200.0],
        },
        schema={
            "reference_date": pl.Date,
            "bond_type": pl.Utf8,
            "maturity_date": pl.Date,
            "buy_price": pl.Float64,
        },
    )
    out = tesouro_direto.to_observations(df)
    assert out["indicator_id"][0] == "td:Tesouro IPCA+:2035-05-15:buy_price"
