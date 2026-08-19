import pytest

from vlrdevapi.commons.regions import (
    COUNTRY_TO_REGION,
    SUBREGION_TO_REGION,
    VALID_REGIONS,
    resolve_country_to_region,
    resolve_subregion_to_region,
)


class TestValidRegions:
    def test_has_five_entries(self):
        assert len(VALID_REGIONS) == 5

    def test_contains_expected(self):
        expected = {"Americas", "EMEA", "Pacific", "China", "International"}
        assert set(VALID_REGIONS) == expected


class TestSubregionToRegion:
    @pytest.mark.parametrize(
        ("subregion", "expected"),
        [
            ("North America", "Americas"),
            ("Brazil", "Americas"),
            ("LATAM North", "Americas"),
            ("LATAM South", "Americas"),
            ("LATAM", "Americas"),
            ("France", "EMEA"),
            ("DACH", "EMEA"),
            ("Spain", "EMEA"),
            ("NORTH//EAST", "EMEA"),
            ("Türkiye", "EMEA"),
            ("Turkey", "EMEA"),
            ("MENA", "EMEA"),
            ("Korea", "Pacific"),
            ("Japan", "Pacific"),
            ("Southeast Asia", "Pacific"),
            ("South Asia", "Pacific"),
            ("Oceania", "Pacific"),
        ],
    )
    def test_known_subregions(self, subregion, expected):
        assert resolve_subregion_to_region(subregion) == expected

    def test_unknown_returns_none(self):
        assert resolve_subregion_to_region("Atlantis") is None

    def test_empty_string_returns_none(self):
        assert resolve_subregion_to_region("") is None

    def test_case_sensitive(self):
        assert resolve_subregion_to_region("japan") is None
        assert resolve_subregion_to_region("JAPAN") is None

    def test_all_values_are_valid_regions(self):
        for region in SUBREGION_TO_REGION.values():
            assert region in VALID_REGIONS, f"Invalid region: {region}"


class TestCountryToRegion:
    @pytest.mark.parametrize(
        ("country", "expected"),
        [
            # Pacific
            ("Japan", "Pacific"),
            ("South Korea", "Pacific"),
            ("Thailand", "Pacific"),
            ("Vietnam", "Pacific"),
            ("Australia", "Pacific"),
            ("India", "Pacific"),
            ("Singapore", "Pacific"),
            ("Philippines", "Pacific"),
            ("Indonesia", "Pacific"),
            # Americas
            ("United States", "Americas"),
            ("Canada", "Americas"),
            ("Mexico", "Americas"),
            ("Brazil", "Americas"),
            ("Argentina", "Americas"),
            ("Chile", "Americas"),
            ("Colombia", "Americas"),
            ("Puerto Rico", "Americas"),
            # EMEA
            ("Germany", "EMEA"),
            ("United Kingdom", "EMEA"),
            ("France", "EMEA"),
            ("Spain", "EMEA"),
            ("Turkey", "EMEA"),
            ("Saudi Arabia", "EMEA"),
            ("Egypt", "EMEA"),
            ("South Africa", "EMEA"),
            ("Russia", "EMEA"),
            ("Israel", "EMEA"),
            ("Pakistan", "EMEA"),
            # China
            ("China", "China"),
        ],
    )
    def test_known_countries(self, country, expected):
        assert resolve_country_to_region(country) == expected

    def test_unknown_returns_none(self):
        assert resolve_country_to_region("Atlantis") is None

    def test_empty_string_returns_none(self):
        assert resolve_country_to_region("") is None

    def test_case_sensitive(self):
        assert resolve_country_to_region("japan") is None
        assert resolve_country_to_region("JAPAN") is None

    def test_all_values_are_valid_regions(self):
        for region in COUNTRY_TO_REGION.values():
            assert region in VALID_REGIONS, f"Invalid region: {region}"
