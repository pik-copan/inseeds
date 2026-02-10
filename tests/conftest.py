import os
import pickle
import sys

import pytest

# Fix for Intel OneAPI causing pandas import hangs on HPC
# Set single-threaded Intel libraries to prevent hanging
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"


@pytest.fixture(scope="session")
def test_path():
    """Fixture for the test path."""
    return os.path.dirname(os.path.abspath(__file__))


def _patch_lpjml_for_testing(lpjml_obj, test_path):
    """Patch lpjml object with read_input/read_output that read from pickle
    files."""

    if hasattr(lpjml_obj, "config") and lpjml_obj.config is not None:
        from pycoupler.data import LPJmLInputType

        LPJmLInputType.load_config(lpjml_obj.config)

    def read_input():
        with open(f"{test_path}/data/lpjml_input.pkl", "rb") as inp:
            return pickle.load(inp)

    def read_output():
        with open(f"{test_path}/data/lpjml_output.pkl", "rb") as out:
            return pickle.load(out)

    lpjml_obj.read_input = read_input
    lpjml_obj.read_output = read_output
    lpjml_obj.read_historic_output = read_output
    return lpjml_obj


@pytest.fixture(scope="session")
def lpjml_data(test_path):
    """Load LPJmL data once for all tests and patch for pickle-based
    testing."""

    with open(f"{test_path}/data/lpjml.pkl", "rb") as lpj:
        data = pickle.load(lpj)
    return _patch_lpjml_for_testing(data, test_path)


@pytest.fixture(scope="session")
def regions_model_instance(lpjml_data):
    """Create regions model instance once for all tests."""
    from inseeds.realisations.regenerative_tillage_regions import Model

    return Model(lpjml=lpjml_data)


@pytest.fixture(scope="session")
def regular_model_instance(lpjml_data):
    """Create regular model instance once for all tests."""
    from inseeds.realisations.regenerative_tillage import Model

    return Model(lpjml=lpjml_data)


@pytest.fixture(scope="session")
def run_regions_model_instance(regions_model_instance):
    """Run the regions model once and return it."""
    for year in regions_model_instance.lpjml.get_sim_years():
        regions_model_instance.update(year)
    return regions_model_instance


@pytest.fixture(scope="session")
def quick_model_instance(lpjml_data):
    """Create a model instance without running simulation - for quick tests."""
    from inseeds.realisations.regenerative_tillage_regions import Model

    return Model(lpjml=lpjml_data)


@pytest.fixture(scope="session")
def quick_regular_model_instance(lpjml_data):
    """Create a regular model instance without running simulation - for quick
    tests."""
    from inseeds.realisations.regenerative_tillage import Model

    return Model(lpjml=lpjml_data)


@pytest.fixture(scope="session")
def run_regular_model_instance(regular_model_instance):
    """Run the regular model once and return it."""
    for year in regular_model_instance.lpjml.get_sim_years():
        regular_model_instance.update(year)
    return regular_model_instance


@pytest.fixture(scope="session")
def single_step_model_instance(quick_model_instance):
    """Run just one simulation step for tests that need some simulation."""
    initial_year = list(quick_model_instance.lpjml.get_sim_years())[0]
    quick_model_instance.update(initial_year)
    return quick_model_instance


@pytest.fixture(scope="session")
def cached_output_table(run_regions_model_instance):
    """Pre-compute and cache the expensive output table."""
    return run_regions_model_instance.output_table.copy()


@pytest.fixture(scope="session")
def cached_regular_output_table(run_regular_model_instance):
    """Pre-compute and cache the expensive output table for regular model."""
    return run_regular_model_instance.output_table.copy()


@pytest.fixture(scope="session")
def cached_test_output_table(test_path):
    """Pre-load and cache the expected test output CSV."""
    import pandas as pd

    test_output = pd.read_csv(f"{test_path}/data/test_output_table.csv")
    return test_output.where(test_output.notna(), None)


@pytest.fixture(scope="session")
def minimal_model_instance(lpjml_data):
    """Create minimal model instance with minimal data for structure tests."""
    from inseeds.realisations.regenerative_tillage_regions import Model

    # Create model but don't initialize expensive components
    model = Model(lpjml=lpjml_data)
    return model


def pytest_configure(config):
    """Mark that we're running from pytest so pycopanlpjml uses test mode."""
    sys._called_from_test = True


def pytest_unconfigure(config):
    """Clean up test marker after pytest exits."""
    if hasattr(sys, "_called_from_test"):
        del sys._called_from_test
