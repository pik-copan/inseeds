"""Entity base class - functionality migrated to pycopanlpjml."""

from pycopanlpjml.output import OutputDefinitionMixin


class Entity(OutputDefinitionMixin):
    """Define properties - functionality migrated to pycopanlpjml.

    Inherits from pycopanlpjml's OutputDefinitionMixin to get default
    get_defined_outputs() implementation. The config key is determined
    from the entity class name (e.g., 'Farmer' -> 'farmer',
    'Consumer' -> 'consumer').
    """

    def __init__(self, model=None):
        self.model = model

    @property
    def model(self):
        """Reference to the Model instance."""
        return self._model if hasattr(self, "_model") else None

    @model.setter
    def model(self, value):
        """Set the model reference."""
        self._model = value

    def update(self, t):
        pass
