"""Tests for DataContract definitions."""

from datetime import date

import polars as pl
import pytest

from quantilica.catalog import (
    INDICATOR_CONTRACT,
    OBSERVATION_CONTRACT,
    DataCategory,
    Frequency,
    IndicatorEntry,
    entries_to_frame,
)


def test_observation_contract_valid():
    df = pl.DataFrame(
        {
            "indicator_id": ["bcb-sgs:12"],
            "date": [date(2025, 1, 1)],
            "geo_id": [None],
            "value": [1.5],
            "date_end": [None],
        },
        schema={
            "indicator_id": pl.Utf8,
            "date": pl.Date,
            "geo_id": pl.Utf8,
            "value": pl.Float64,
            "date_end": pl.Date,
        },
    )
    OBSERVATION_CONTRACT.validate(df)


def test_observation_contract_missing_required():
    df = pl.DataFrame({"date": [date(2025, 1, 1)]})
    with pytest.raises(ValueError, match="indicator_id"):
        OBSERVATION_CONTRACT.validate(df)


def test_observation_contract_wrong_type():
    df = pl.DataFrame(
        {
            "indicator_id": ["bcb-sgs:12"],
            "date": [date(2025, 1, 1)],
            "geo_id": [None],
            "value": ["not-a-float"],
            "date_end": [None],
        },
        schema={
            "indicator_id": pl.Utf8,
            "date": pl.Date,
            "geo_id": pl.Utf8,
            "value": pl.Utf8,
            "date_end": pl.Date,
        },
    )
    with pytest.raises(TypeError):
        OBSERVATION_CONTRACT.validate(df)


def test_indicator_contract_valid():
    df = pl.DataFrame(
        {
            "indicator_id": ["bcb-sgs:12"],
            "source_id": ["bcb"],
            "source_dataset_id": ["bcb-sgs"],
            "name": ["Taxa Selic"],
            "category": ["monetary"],
            "subcategory": [None],
            "unit": ["%"],
            "frequency": ["daily"],
            "geo_level": [None],
            "description": [None],
        },
        schema={
            "indicator_id": pl.Utf8,
            "source_id": pl.Utf8,
            "source_dataset_id": pl.Utf8,
            "name": pl.Utf8,
            "category": pl.Utf8,
            "subcategory": pl.Utf8,
            "unit": pl.Utf8,
            "frequency": pl.Utf8,
            "geo_level": pl.Utf8,
            "description": pl.Utf8,
        },
    )
    INDICATOR_CONTRACT.validate(df)



def test_entries_to_frame_roundtrip():
    entry = IndicatorEntry(
        indicator_id="bcb-sgs:12",
        source_id="bcb",
        source_dataset_id="bcb-sgs",
        name="Taxa Selic",
        category=DataCategory.MONETARY,
        unit="%",
        frequency=Frequency.DAILY,
        geo_level="country",
    )
    df = entries_to_frame([entry])
    assert df.shape == (1, 10)
    assert df["indicator_id"][0] == "bcb-sgs:12"
    assert df["category"][0] == "monetary"
    assert df["frequency"][0] == "daily"


def test_entries_to_frame_empty():
    df = entries_to_frame([])
    assert df.shape[0] == 0
    assert "indicator_id" in df.columns
