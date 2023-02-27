# (c) Copyright 2013, 2014, University of Manchester
#
# HydraPlatform is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# HydraPlatform is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with HydraPlatform.  If not, see <http://www.gnu.org/licenses/>
#
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from spyne.model.primitive import Unicode, Boolean, Decimal, Integer, Float
from spyne.model.complex import Array as SpyneArray, ComplexModel
from spyne.decorator import rpc
from spyne.util.dictdoc import get_object_as_dict
from .service import HydraService
from .complexmodels import Unit, Dimension
from hydra_base.lib import units
import json

from hydra_base.lib.objects import JSONObject
import logging
log = logging.getLogger(__name__)

class UnitService(HydraService):
    """
    +---------------------------+
    | DIMENSION FUNCTIONS - GET |
    +---------------------------+
    """
    @rpc(Integer, Unicode(pattern='[YN]'), _returns=Dimension)
    def get_dimension(ctx, dimension_id, do_accept_dimension_id_none):
        """
            Gets the dimension details and the list of all units assigned to the dimension.
        """
        accept_null_dimension = do_accept_dimension_id_none == 'Y'
        dimension = units.get_dimension(dimension_id,
                                        do_accept_dimension_id_none=accept_null_dimension,
                                        **ctx.in_header.__dict__)

        return Dimension(dimension)

    @rpc(Unicode, _returns=Dimension)
    def get_dimension_by_name(ctx, dimension_name):
        """
            Gets the dimension details and the list of all units assigned to the dimension.
        """
        dimension = units.get_dimension_by_name(dimension_name, **ctx.in_header.__dict__)

        return Dimension(dimension)

    @rpc(_returns=SpyneArray(Dimension))
    def get_dimensions(ctx):
        """
            Gets a list of all physical dimensions available on the server.
        """
        dim_list = units.get_dimensions(**ctx.in_header.__dict__)
        return [Dimension(d) for d in dim_list]


    @rpc(_returns=Dimension)
    def get_empty_dimension(ctx):
        empty_dimension = units.get_empty_dimension()
        return Dimension(empty_dimension)

    """
    +----------------------+
    | UNIT FUNCTIONS - GET |
    +----------------------+
    """
    @rpc(Integer, _returns=Unit)
    def get_unit(ctx, unit_id):
        """
            Gets the Unit details
        """
        unit = units.get_unit(unit_id, **ctx.in_header.__dict__)

        return Unit(unit)

    @rpc(Integer, _returns=Unit)
    def get_unit_by_abbreviation(ctx, unit_abbr):
        """
            Gets the Unit details
        """
        unit = units.get_unit_by_abbreviation(unit_abbr, **ctx.in_header.__dict__)

        return Unit(unit)

    @rpc(_returns=SpyneArray(Unit))
    def get_units(ctx):
        """
            Get a list of all units corresponding to a physical dimension.
        """
        unit_list = units.get_units(**ctx.in_header.__dict__)
        return [Unit(u) for u in unit_list]

    @rpc(Integer, Unicode(pattern="[YN]"), _returns=Dimension)
    def get_dimension_by_unit_id(ctx, unit_id, do_accept_unit_id_none):
        """
            Return the physical dimension a given unit id refers to.
            if do_accept_unit_id_none is 'N', it raises an exception
            if unit_id is not valid or None

            if do_accept_unit_id_none is 'Y', and unit_id is None,
            the function returns a Dimension with id None
            (unit_id can be none in some cases)
        """
        accept_null_unit = do_accept_unit_id_none == 'Y'
        unit_dimension = units.get_dimension_by_unit_id(unit_id,
            do_accept_unit_id_none=accept_null_unit,
            **ctx.in_header.__dict__)
        return Dimension(unit_dimension)

    @rpc(Unicode, _returns=Dimension)
    def get_dimension_by_unit_measure_or_abbreviation(ctx, measure_or_unit_abbreviation):
        """
            Return the physical dimension a given unit abbreviation of a measure,
            or the measure itself, refers to.

            The search key is the abbreviation or the full measure

            Args:
                Unit measure or abbreviation
            Returns:
                Dimension
            Raises:
                HydraError if the unit is not found, or multiple dimensions are found
        """
        unit_dimension = units.get_dimension_by_unit_measure_or_abbreviation(
            measure_or_unit_abbreviation,
            **ctx.in_header.__dict__)
        return Dimension(unit_dimension)
    """
    +---------------------------------------+
    | DIMENSION FUNCTIONS - ADD - DEL - UPD |
    +---------------------------------------+
    """
    @rpc(Dimension, _returns=Dimension)
    def add_dimension(ctx, dimension):
        """Add a physical dimensions (such as ``Volume`` or ``Speed``) to the
        servers list of dimensions. If the dimension already exists, nothing is
        done.
        """
        result = units.add_dimension(JSONObject(dimension), **ctx.in_header.__dict__)
        return Dimension(result)

    @rpc(Dimension, _returns=Dimension)
    def update_dimension(ctx, dimension):
        """
            update a physical dimensions (such as ``Volume`` or ``Speed``) to the
            servers list of dimensions.
        """
        result = units.update_dimension(JSONObject(dimension), **ctx.in_header.__dict__)
        return Dimension(result)

    @rpc(Integer, _returns=Boolean)
    def delete_dimension(ctx, dimension_id):
        """Delete a physical dimension from the list of dimensions. Please note
        that deleting works only for dimensions listed in the custom file.
        """
        result = units.delete_dimension(dimension_id, **ctx.in_header.__dict__)
        return 'OK'
    """
    +----------------------------------+
    | UNIT FUNCTIONS - ADD - DEL - UPD |
    +----------------------------------+
    """
    @rpc(Unit, _returns=Unit)
    def add_unit(ctx, unit):
        """Add a physical unit to the servers list of units. The Hydra server
        provides a complex model ``Unit`` which should be used to add a unit.

        A minimal example:

        .. code-block:: python

            from HydraLib import PluginLib

            cli = PluginLib.connect()

            new_unit = cli.factory.create('hyd:Unit')
            new_unit.name = 'Teaspoons per second'
            new_unit.abbr = 'tsp s^-1'
            new_unit.cf = 0               # Constant conversion factor
            new_unit.lf = 1.47867648e-05  # Linear conversion factor
            new_unit.dimension = 'Volumetric flow rate'
            new_unit.info = 'A flow of one teaspoon per second.'

            cli.service.add_unit(new_unit)
        """
        # Convert the complex model into a dict
        #unitdict = get_object_as_dict(unit, Unit)#
        result = units.add_unit(JSONObject(unit), **ctx.in_header.__dict__)
        return result


    @rpc(Unit, _returns=Unit)
    def update_unit(ctx, unit):
        """Update an existing unit added to the custom unit collection. Please
        not that units built in to the library can not be updated.
        """
        result = units.update_unit(JSONObject(unit), **ctx.in_header.__dict__)
        return Unit(result)


    @rpc(Integer, _returns=Boolean)
    def delete_unit(ctx, unit_id):
        """Delete a unit from the custom unit collection.
        """
        result = units.delete_unit(unit_id, **ctx.in_header.__dict__)
        return 'OK'


    # @rpc(Decimal(min_occurs=1, max_occurs="unbounded"),
    #      Unicode, Unicode,
    #      _returns=Decimal(min_occurs="1", max_occurs="unbounded"))
    @rpc(Decimal(min_occurs=1, max_occurs="unbounded"),Unicode, Unicode, _returns=SpyneArray(Float))
    def convert_units(ctx, values, unit1, unit2):
        """
            Convert a list of values from one unit to another one.

        Example::

            >>> cli = PluginLib.connect()
            >>> cli.service.convert_units(20.0, 'm', 'km')
            0.02
        """
        if not isinstance(values, list):
            values = [values]
        return_array = units.convert_units(values, unit1, unit2)
        return return_array

    @rpc(Decimal,Unicode, Unicode, _returns=SpyneArray(Decimal))
    def convert_unit(ctx, value, unit1, unit2):
        """
        Convert a SINGLE value from one unit to another one.

        Example::

            >>> cli = PluginLib.connect()
            >>> cli.service.convert_units(20.0, 'm', 'km')
            0.02
        """
        values_to_return = units.convert_units(value, unit1, unit2, **ctx.in_header.__dict__)
        return values_to_return

    @rpc(Unicode, Unicode, _returns=Boolean)
    def check_consistency(ctx, unit, dimension):
        """Check if a given units corresponds to a physical dimension.
        """
        return units.check_consistency(unit, dimension, **ctx.in_header.__dict__)

    @rpc(Integer, _returns=Boolean)
    def is_global_dimension(ctx, dimension_id):
        """
            Returns True if the dimension is global, False otherwise
        """
        return units.is_global_dimension(dimension_id, **ctx.in_header.__dict__)


    @rpc(Integer, _returns=Boolean)
    def is_global_unit(ctx, unit_id):
        """
            Returns True if the dimension is global, False otherwise
        """
        return units.is_global_unit(unit_id, **ctx.in_header.__dict__)


    @rpc(Integer, Unicode, _returns=Integer)
    def convert_dataset(ctx, dataset_id, to_unit):
        """Convert a whole dataset (specified by 'dataset_id' to new unit
        ('to_unit').
        """
        return units.convert_dataset(dataset_id, to_unit, **ctx.in_header.__dict__)
