"""Unit tests for base components (Entity, etc.)."""

import pytest

from inseeds.components.base import Entity


class TestEntity:
    """Tests for the base Entity class."""

    def test_entity_init_default(self):
        """Entity() should initialize with model=None."""
        entity = Entity()
        assert entity.model is None

    def test_entity_model_setter_getter(self):
        """Entity model can be set and retrieved."""
        entity = Entity()
        obj = object()
        entity.model = obj
        assert entity.model is obj

    def test_entity_update_noop(self):
        """Entity.update(t) should be a no-op (does not raise)."""
        entity = Entity()
        entity.update(2020)  # Should not raise
