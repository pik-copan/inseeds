"""InSEEDS - Integrated Social-Ecological Resilient Land Systems Model."""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("inseeds")
except PackageNotFoundError:
    __version__ = "unknown"
