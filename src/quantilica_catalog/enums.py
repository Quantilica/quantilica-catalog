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
    YEARLY = "yearly"
    IRREGULAR = "irregular"


class GeoLevel(str, Enum):
    COUNTRY = "country"
    REGION = "region"
    STATE = "state"
    MUNICIPALITY = "municipality"
    STATION = "station"
