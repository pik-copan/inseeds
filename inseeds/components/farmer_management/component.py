"""Model mixing class for inseeds_farmer_management
"""

# This file is part of pycopancore.
#
# Copyright (C) 2016-2017 by COPAN team at Potsdam Institute for Climate
# Impact Research
#
# URL: <http://www.pik-potsdam.de/copan/software>
# Contact: core@pik-potsdam.de
# License: BSD 2-clause license

from . import documentation as doc

# import all needed entity type implementation classes:
from . import World, Farmer


class Component(doc.Component):
    """Model mixin class."""

    # mixins provided by this model component:
    entity_types = [World, Farmer]
    """list of entity types augmented by this component"""
    process_taxa = []
    """list of process taxa augmented by this component"""
