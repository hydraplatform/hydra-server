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

from spyne.model.primitive import Unicode, Boolean, Decimal, Integer
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
    """
    @rpc(_returns=SpyneArray(Unicode))
    def get_dimensions(ctx):
        """
            Get a list of all physical dimensions available on the server.
        """
        dim_list = units.get_dimensions(**ctx.in_header.__dict__)
        return dim_list

    @rpc(_returns=SpyneArray(Dimension))
    def get_all_dimensions(ctx):
        """
            Get a list of all physical dimensions available on the server.
        """
        dimdict = units.get_all_dimensions(**ctx.in_header.__dict__)
        dimens = []
        for dim_name, unit_list in dimdict.items():
            dim = Dimension()
            dim.name = dim_name
            dim.units = unit_list
            dimens.append(dim)
            # dimens.append({"name":dim_name, "units":unit_list})
        return dimens

    @rpc(Unicode, _returns=SpyneArray(Unit))
    def get_units(ctx, dimension):
        """
            Get a list of all units corresponding to a physical dimension.
        """
        log.info("Server - get_units - dimension={}".format(dimension))
        unit_list = units.get_units(dimension, **ctx.in_header.__dict__)
        return unit_list


    @rpc(Unicode, _returns=SpyneArray(Unicode))
    def get_dimension(ctx, dimension):
        """
            Get a list of all units assigned to a dimension.
        """
        units_list = units.get_dimension(dimension, **ctx.in_header.__dict__)
        return units_list

    @rpc(Unicode, _returns=Unicode)
    def get_dimension_data(ctx, dimension_name,**kwargs):
        """
            Given a dimension returns all its data
        """
        dimension_data = units.get_dimension_data(dimension_name, **ctx.in_header.__dict__)

        return json.dumps(dimension_data)


    @rpc(Unicode, _returns=Unicode)
    def get_unit_dimension(ctx, unit1):
        """Get the corresponding physical dimension for a given unit.

        Example::

            >>> cli = PluginLib.connect()
            >>> cli.service.get_dimension('m')
            Length
        """
        dim = units.get_unit_dimension(unit1, **ctx.in_header.__dict__)

        return dim

    # @rpc(Unicode, _returns=Unicode)
    # def get_unit_dimension(ctx, unit1):
    #     """Get the corresponding physical dimension for a given unit.
    #
    #     Example::
    #
    #         >>> cli = PluginLib.connect()
    #         >>> cli.service.get_dimension('m')
    #         Length
    #     """
    #     dim = units.get_unit_dimension(unit1, **ctx.in_header.__dict__)
    #
    #     return dim



    @rpc(Dimension, _returns=Boolean)
    def add_dimension(ctx, dimension):
        """Add a physical dimensions (such as ``Volume`` or ``Speed``) to the
        servers list of dimensions. If the dimension already exists, nothing is
        done.
        """
        # try:
        #     # Trying to decode as a json
        #     dimension = json.loads(dimension)
        # except Exception as e:
        #     # It is a straight string
        #     pass
        result = units.add_dimension(JSONObject(dimension), **ctx.in_header.__dict__)
        log.info("add_dimension %s", result)
        return json.dumps(result)

    @rpc(Dimension, _returns=Boolean)
    def update_dimension(ctx, dimension):
        """
            update a physical dimensions (such as ``Volume`` or ``Speed``) to the
            servers list of dimensions.
        """
        #dimension = json.loads(dimension)
        result = units.update_dimension(JSONObject(dimension), **ctx.in_header.__dict__)
        return json.dumps(result)

    @rpc(Dimension, _returns=Boolean)
    def delete_dimension(ctx, dimension):
        """Delete a physical dimension from the list of dimensions. Please note
        that deleting works only for dimensions listed in the custom file.
        """
        # try:
        #     # Trying to decode as a json
        #     dimension = json.loads(dimension)
        # except Exception as e:
        #     # It is a straight string
        #     pass
        result = units.delete_dimension(JSONObject(dimension), **ctx.in_header.__dict__)
        return str(result)

    @rpc(Unit, _returns=Boolean)
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
        log.info("add_unit - unit = %s", unit)
        # try:
        #     # Trying to decode as a json
        #     unit = json.loads(unit)
        # except Exception as e:
        #     # It is a straight string
        #     pass
        unitdict = get_object_as_dict(unit, Unit)
        units.add_unit(unitdict, **ctx.in_header.__dict__)
        return True

    @rpc(Unit, _returns=Boolean)
    def update_unit(ctx, unit):
        """Update an existing unit added to the custom unit collection. Please
        not that units built in to the library can not be updated.
        """
        # try:
        #     # Trying to decode as a json
        #     unit = json.loads(unit)
        # except Exception as e:
        #     # It is a straight string
        #     pass
        unitdict = get_object_as_dict(unit, Unit)
        result = units.update_unit(unitdict, **ctx.in_header.__dict__)
        return result

    @rpc(Unit, _returns=Boolean)
    def delete_unit(ctx, unit):
        """Delete a unit from the custom unit collection.
        """
        # try:
        #     # Trying to decode as a json
        #     unit = json.loads(unit)
        # except Exception as e:
        #     # It is a straight string
        #     pass
        unitdict = get_object_as_dict(unit, Unit)
        result = units.delete_unit(unitdict, **ctx.in_header.__dict__)
        return result

    # @rpc(Decimal(min_occurs=1, max_occurs="unbounded"),
    #      Unicode, Unicode,
    #      _returns=Decimal(min_occurs="1", max_occurs="unbounded"))
    @rpc(SpyneArray(Decimal),Unicode, Unicode, _returns=SpyneArray(Decimal))
    def convert_units(ctx, values, unit1, unit2):
        """
            Convert a list of values from one unit to another one.

        Example::

            >>> cli = PluginLib.connect()
            >>> cli.service.convert_units(20.0, 'm', 'km')
            0.02
        """
        return_array = [units.convert_units(v, unit1, unit2)[0] for v in values]
        # log.info("convert_units result %s", return_array)
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
        # log.info("convert_unit %s from %s to %s", value, unit1, unit2)
        values_to_return = units.convert_units(value, unit1, unit2, **ctx.in_header.__dict__)
        # log.info("convert_unit result %s", values_to_return)
        return values_to_return

    @rpc(Unicode, Unicode, _returns=Boolean)
    def check_consistency(ctx, unit, dimension):
        """Check if a given units corresponds to a physical dimension.
        """
        return units.check_consistency(unit, dimension, **ctx.in_header.__dict__)

    @rpc(Dimension, _returns=Boolean)
    def is_global_dimension(ctx, dimension):
        """
            Returns True if the dimension is global, False otherwise
        """
        return units.is_global_dimension(JSONObject(dimension), **ctx.in_header.__dict__)


    @rpc(Unit, _returns=Boolean)
    def is_global_unit(ctx, unit):
        """
            Returns True if the dimension is global, False otherwise
        """
        return units.is_global_unit(JSONObject(unit), **ctx.in_header.__dict__)




    @rpc(Integer, Unicode, _returns=Integer)
    def convert_dataset(ctx, dataset_id, to_unit):
        """Convert a whole dataset (specified by 'dataset_id' to new unit
        ('to_unit').
        """
        return units.convert_dataset(dataset_id, to_unit, **ctx.in_header.__dict__)
