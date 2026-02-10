"""Unit tests for farming components (Farmer, TillageFarmer, AFT, sigmoid)."""

import numpy as np
import pytest

from inseeds.components.farming import Farmer, TillageFarmer
from inseeds.components.farming.farmer import AFT
from inseeds.components.farming.tillage_farmer import sigmoid


class TestSigmoid:
    """Tests for the sigmoid helper function."""

    def test_sigmoid_zero_returns_half(self):
        """sigmoid(0) should return 0.5."""
        assert sigmoid(0) == pytest.approx(0.5)

    def test_sigmoid_positive_increases(self):
        """sigmoid(x) for x > 0 should be > 0.5."""
        assert sigmoid(1) > 0.5
        assert sigmoid(10) == pytest.approx(1.0, abs=1e-6)

    def test_sigmoid_negative_decreases(self):
        """sigmoid(x) for x < 0 should be < 0.5."""
        assert sigmoid(-1) < 0.5
        assert sigmoid(-10) == pytest.approx(0.0, abs=1e-6)

    def test_sigmoid_bounds(self):
        """sigmoid output should be in [0, 1]."""
        for x in [-100, -10, -1, 0, 1, 10, 100]:
            y = sigmoid(x)
            assert 0 <= y <= 1


class TestAFT:
    """Tests for the AFT (Agent Farmer Type) enum."""

    def test_aft_values(self):
        """AFT should have traditionalist=0 and pioneer=1."""
        assert AFT.traditionalist.value == 0
        assert AFT.pioneer.value == 1

    def test_aft_random_returns_valid_type(self):
        """AFT.random() should return a valid AFT enum."""
        for _ in range(20):
            aft = AFT.random(pioneer_share=0.5)
            assert aft in (AFT.traditionalist, AFT.pioneer)

    def test_aft_random_pioneer_share_zero(self):
        """AFT.random(pioneer_share=0) should always return traditionalist."""
        for _ in range(20):
            assert AFT.random(pioneer_share=0) == AFT.traditionalist

    def test_aft_random_pioneer_share_one(self):
        """AFT.random(pioneer_share=1) should always return pioneer."""
        for _ in range(20):
            assert AFT.random(pioneer_share=1) == AFT.pioneer


class TestTillageFarmerSplitNeighbourhood:
    """Tests for TillageFarmer.split_neighbourhood and
    split_neighbourhood_status."""

    def test_split_neighbourhood_empty(self, quick_model_instance):
        """split_neighbourhood with empty neighbourhood returns empty lists."""
        farmers = getattr(quick_model_instance, "_farmers", [])
        if not farmers:
            pytest.skip("No farmers in test model")
        farmer = farmers[0]
        # Temporarily clear neighbourhood
        original_nb = farmer.neighbourhood
        farmer.neighbourhood = []
        first_nb, second_nb = farmer.split_neighbourhood("tillage")
        farmer.neighbourhood = original_nb
        assert first_nb == []
        assert second_nb == []

    def test_split_neighbourhood_splits_by_attribute(
        self, quick_model_instance
    ):
        """split_neighbourhood splits neighbours by tillage (0 vs 1)."""
        farmers = getattr(quick_model_instance, "_farmers", [])
        if len(farmers) < 2:
            pytest.skip("Need at least 2 farmers for neighbourhood test")
        farmer = farmers[0]
        if not farmer.neighbourhood:
            pytest.skip("Farmer has no neighbours")
        first_nb, second_nb = farmer.split_neighbourhood("tillage")
        for n in first_nb:
            assert n.tillage == 0
        for n in second_nb:
            assert n.tillage == 1
        assert len(first_nb) + len(second_nb) == len(farmer.neighbourhood)

    def test_split_neighbourhood_status_returns_tuple(
        self, quick_model_instance
    ):
        """split_neighbourhood_status returns (first_avg, second_avg)."""
        farmers = getattr(quick_model_instance, "_farmers", [])
        if not farmers:
            pytest.skip("No farmers in test model")
        farmer = farmers[0]
        result = farmer.split_neighbourhood_status("cropyield")
        assert isinstance(result, tuple)
        assert len(result) == 2
        first_var, second_var = result
        # With or without neighbours, result should be numeric or nan
        assert np.isnan(first_var) or isinstance(first_var, (int, float))
        assert np.isnan(second_var) or isinstance(second_var, (int, float))


class TestTillageFarmerTPBProperties:
    """Tests for TPB-based properties (attitude, social_norm)."""

    def test_attitude_is_in_valid_range(self, quick_model_instance):
        """attitude should be in [0, 1] or NaN (sigmoid output; NaN from edge
        cases)."""

        farmers = getattr(quick_model_instance, "_farmers", [])
        if not farmers:
            pytest.skip("No farmers in test model")
        for farmer in farmers[:5]:
            att = farmer.attitude
            if np.isfinite(att):
                assert 0 <= att <= 1, f"attitude={att} out of range"

    def test_social_norm_empty_neighbourhood(self, quick_model_instance):
        """social_norm with empty neighbourhood returns value in [0, 1]."""
        farmers = getattr(quick_model_instance, "_farmers", [])
        if not farmers:
            pytest.skip("No farmers in test model")
        farmer = farmers[0]
        original_nb = farmer.neighbourhood
        farmer.neighbourhood = []
        try:
            norm = farmer.social_norm
            assert 0 <= norm <= 1, f"social_norm={norm} out of [0,1]"
        finally:
            farmer.neighbourhood = original_nb

    def test_social_norm_with_neighbours(self, quick_model_instance):
        """social_norm with neighbours returns value in [0, 1]."""
        farmers = getattr(quick_model_instance, "_farmers", [])
        if not farmers:
            pytest.skip("No farmers in test model")
        farmer = next((f for f in farmers if f.neighbourhood), None)
        if farmer is None:
            pytest.skip("No farmer with neighbours")
        norm = farmer.social_norm
        assert 0 <= norm <= 1


class TestTillageFarmerUpdate:
    """Tests for TillageFarmer.update() behaviour."""

    def test_farmers_have_tillage_attribute(self, quick_model_instance):
        """Farmers should have tillage attribute (0 or 1)."""
        farmers = getattr(quick_model_instance, "_farmers", [])
        if not farmers:
            pytest.skip("No farmers in test model")
        for farmer in farmers[:3]:
            assert hasattr(farmer, "tillage")
            assert farmer.tillage in (0, 1)

    def test_farmers_have_tpb_attribute(self, quick_model_instance):
        """TillageFarmer should have tpb attribute after init."""
        farmers = getattr(quick_model_instance, "_farmers", [])
        if not farmers:
            pytest.skip("No farmers in test model")
        farmer = farmers[0]
        assert hasattr(farmer, "tpb")
        assert isinstance(farmer.tpb, (int, float))


class TestFarmingComponentsImport:
    """Tests for farming component imports and structure."""

    def test_farmer_tillage_farmer_hierarchy(self):
        """TillageFarmer should be a subclass of Farmer."""
        assert issubclass(TillageFarmer, Farmer)

    def test_farming_exports(self):
        """Farming module should export expected classes."""
        from inseeds.components import farming

        assert hasattr(farming, "Farmer")
        assert hasattr(farming, "TillageFarmer")
        assert hasattr(farming, "Cell")
        assert hasattr(farming, "Region")
        assert hasattr(farming, "Country")
        assert hasattr(farming, "World")
