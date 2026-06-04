"""Controlled vocabularies for the Quantilica unified catalog."""

from __future__ import annotations

from enum import Enum


class DataCategory(str, Enum):
    MONETARY = "monetary"
    FISCAL = "fiscal"
    FINANCIAL = "financial"
    CLIMATE = "climate"
    LABOR = "labor"
    TRADE = "trade"
    HEALTH = "health"
    DEMOGRAPHIC = "demographic"
    ECONOMIC = "economic"
    PRICES = "prices"


class Frequency(str, Enum):
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMI_ANNUAL = "semi_annual"
    ROLLING_QUARTERLY = "rolling_quarterly"
    YEARLY = "yearly"
    MULTI_YEAR = "multi_year"
    IRREGULAR = "irregular"


class GeoType(str, Enum):
    TERRITORY = "territory"
    STATION = "station"
    WATERSHED = "watershed"
    BIOME = "biome"
    HEALTH_REGION = "health_region"
    CENSUS_SECTOR = "census_sector"


class RelType(str, Enum):
    ADMINISTRATIVE_PARENT = "administrative_parent"
    CONTAINS = "contains"
    OVERLAPS = "overlaps"
    BORDERS = "borders"


class GeoSystem(str, Enum):
    IBGE_TRADITIONAL = "ibge_traditional"
    IBGE_RGINT = "ibge_rgint"
    IBGE_CENSUS = "ibge_census"
    DATASUS_HEALTH = "datasus_health"
    ANA_HYDROGRAPHIC = "ana_hydrographic"
    INMET = "inmet"
