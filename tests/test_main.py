"""Tests for main.py entry points."""

import pytest


class TestRegenerativeTillageRegionsMain:
    """Tests for regenerative_tillage_regions/main.py."""

    def test_run_inseeds_importable(self):
        """run_inseeds can be imported from main module."""
        from inseeds.realisations.regenerative_tillage_regions.main import (
            run_inseeds,
        )

        assert callable(run_inseeds)

    def test_run_inseeds_signature(self):
        """run_inseeds accepts config_file argument."""
        from inseeds.realisations.regenerative_tillage_regions.main import (
            run_inseeds,
        )

        import inspect

        sig = inspect.signature(run_inseeds)
        assert "config_file" in sig.parameters


class TestRegenerativeTillageMain:
    """Tests for regenerative_tillage/main.py."""

    def test_run_inseeds_importable(self):
        """run_inseeds can be imported from regenerative_tillage main."""
        from inseeds.realisations.regenerative_tillage.main import run_inseeds

        assert callable(run_inseeds)

    def test_run_inseeds_raises_on_missing_file(self):
        """run_inseeds raises FileNotFoundError for non-existent config."""
        from inseeds.realisations.regenerative_tillage.main import run_inseeds

        with pytest.raises(FileNotFoundError, match="does not exist"):
            run_inseeds("/nonexistent/config.json")
