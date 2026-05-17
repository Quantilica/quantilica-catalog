"""Unified data catalog and canonical observation model for Quantilica."""

from .dims.code import GEO_CODE_CONTRACT, GeoCodeEntry, geo_code_entries_to_frame
from .dims.entity import (
    GEO_ENTITY_CONTRACT,
    GeoEntityEntry,
    census_sector_id,
    country_id,
    district_id,
    geo_entity_entries_to_frame,
    mesoregion_id,
    microregion_id,
    municipality_id,
    region_id,
    state_id,
    station_id,
    subdistrict_id,
)
from .dims.indicator import (
    INDICATOR_CONTRACT,
    IndicatorEntry,
    entries_to_frame,
)
from .dims.relationship import (
    GEO_RELATIONSHIP_CONTRACT,
    GeoRelationshipEntry,
    geo_relationship_entries_to_frame,
    relationships_at,
)
from .adapters.sidra import (
    SIDRA_FREQUENCIA_TO_FREQUENCY,
    SIDRA_RESULT_CONTRACT,
    sidra_frequencia_to_frequency,
)
from .enums import DataCategory, Frequency, GeoSystem, GeoType, RelType
from .facts.observation import OBSERVATION_CONTRACT

__all__ = [
    # Geo — entity
    "GEO_ENTITY_CONTRACT",
    "GeoEntityEntry",
    "geo_entity_entries_to_frame",
    # Geo — relationship
    "GEO_RELATIONSHIP_CONTRACT",
    "GeoRelationshipEntry",
    "geo_relationship_entries_to_frame",
    "relationships_at",
    # Geo — external codes
    "GEO_CODE_CONTRACT",
    "GeoCodeEntry",
    "geo_code_entries_to_frame",
    # geo_id builders
    "country_id",
    "region_id",
    "state_id",
    "mesoregion_id",
    "microregion_id",
    "municipality_id",
    "district_id",
    "subdistrict_id",
    "census_sector_id",
    "station_id",
    # Indicators
    "INDICATOR_CONTRACT",
    "IndicatorEntry",
    "entries_to_frame",
    # Observations
    "OBSERVATION_CONTRACT",
    # Enums
    "DataCategory",
    "Frequency",
    "GeoType",
    "RelType",
    "GeoSystem",
    # SIDRA
    "SIDRA_RESULT_CONTRACT",
    "SIDRA_FREQUENCIA_TO_FREQUENCY",
    "sidra_frequencia_to_frequency",
]
