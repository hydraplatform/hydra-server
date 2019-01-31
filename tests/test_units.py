#!/usr/bin/env python
# -*- coding: utf-8 -*-

# (c) Copyright 2013 to 2017 University of Manchester
#
# HydraPlatform is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# HydraPlatform is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with HydraPlatform.  If not, see <http://www.gnu.org/licenses/>
#

from hydra_client.exception import RequestError
from hydra_base.lib.objects import JSONObject

from fixtures import *
import pytest
import logging
log = logging.getLogger(__name__)
import sys
import json
import util

"""
+----------------------------+
| NEEDED for testing dataset |
+----------------------------+
"""

def arr_to_vector(arr):
    """Reshape a multidimensional array to a vector.
    """
    dim = array_dim(arr)
    tmp_arr = []
    for n in range(len(dim) - 1):
        for inner in arr:
            for i in inner:
                tmp_arr.append(i)
        arr = tmp_arr
        tmp_arr = []
    return arr

def array_dim(arr):
    """Return the size of a multidimansional array.
    """
    dim = []
    while True:
        try:
            dim.append(len(arr))
            arr = arr[0]
        except TypeError:
            return dim

def wrap_item_into_dict(scalar_name, scalar_value):
    """
        Function to wrap arguments inside a dict to manage a bug present in JsonDocument.deserialize
    """
    return {scalar_name: scalar_value}

class TestUnits():
    """
        Test for working with units.
    """
    def test_get_dimensions(self, client):

        dimension_list = client.get_dimensions()
        log.info(dimension_list)
        assert dimension_list is not None and len(dimension_list) != 0, \
            "Could not get a list of dimensions names."

    def test_get_all_dimensions(self, client):

        dimension_list = client.get_all_dimensions()
        log.info(dimension_list)
        assert dimension_list is not None and len(dimension_list) != 0, \
            "Could not get the list of all dimensions."

    def test_get_units(self, client):

        dimension_list = client.get_dimensions() # Dimensions names list
        units_found = 0
        log.info(dimension_list)
        for dimension in dimension_list:
            log.info("test_get_units - dimension = {}".format(dimension))
            units_list = client.get_units(wrap_item_into_dict("dimension", dimension))
            assert units_list is not None, \
                "Could not get a list of units from hydra_base.get_units"
            units_found+=len(units_list)
        assert units_found != 0, \
            "hydra_base.get_units Could not get any units from the source"

    def test_get_dimension(self, client):

        testdim = 'Length'
        resultdim = client.get_dimension(wrap_item_into_dict("dimension", testdim))
        assert len(resultdim) > 0, \
            "Getting dimension for 'kilometers' didn't work."

        with pytest.raises(RequestError):
            #dimension = hb.get_dimension('not-existing-dimension')
            dimension = client.get_dimension(wrap_item_into_dict("dimension", 'not-existing-dimension'))

    def test_get_dimension_data(self, client):

        testdim = 'Length'
        resultdim = client.get_dimension_data(wrap_item_into_dict("dimension_name", testdim))
        log.info("test_get_dimension_data")
        log.info(resultdim)
        resultdim = json.loads(resultdim)
        assert resultdim["name"] == testdim, \
            "Getting dimension for 'kilometers' didn't work."

        with pytest.raises(RequestError):
            dimension = client.get_dimension_data('not-existing-dimension')


    def test_get_unit_dimension(self, client):

        testdim = 'Length'
        testunit = 'km'
        resultdim = client.get_unit_dimension(wrap_item_into_dict("unit1",testunit))

        assert testdim == resultdim, \
            "Getting dimension for 'kilometers' didn't work."

        with pytest.raises(RequestError):
            dimension = client.get_unit_dimension(wrap_item_into_dict("unit1",'not-existing-unit'))

    def test_add_dimension(self, client):

        # Try to add an existing dimension
        testdim = {'name': 'Length'}
        with pytest.raises(RequestError) as excinfo:
            client.add_dimension(wrap_item_into_dict("dimension", testdim))
            #client.add_dimension(wrap_item_into_dict("dimension", json.dumps(testdim)))

        # Add a new dimension
        testdim = {'name':'Electric current'}
        #client.add_dimension(wrap_item_into_dict("dimension", json.dumps(testdim)))
        client.add_dimension(wrap_item_into_dict("dimension", testdim))

        dimension_list = list(client.get_dimensions())
        assert testdim["name"] in dimension_list, \
            "Adding new dimension didn't work as expected."

        # Add a new dimension as scalar
        # testdim = 'Electric test'
        # client.add_dimension(wrap_item_into_dict("dimension", testdim))
        # #client.add_dimension(wrap_item_into_dict("dimension", json.dumps(testdim)))
        #
        # dimension_list = list(client.get_dimensions())
        # assert testdim in dimension_list, \
        #     "Adding new dimension didn't work as expected."


    def test_update_dimension(self, client):
        # Updating existing dimension
        # Add a new dimension
        testdim = {'name':'Electric current'}
        client.add_dimension(wrap_item_into_dict("dimension", testdim))

        testdim = {
                    'name':'Electric current',
                    'description': 'New description Electric current'
                    }
        client.update_dimension(wrap_item_into_dict("dimension", testdim))

        modified_dim = json.loads(client.get_dimension_data(wrap_item_into_dict("dimension_name", testdim["name"])))
        assert modified_dim["description"] == testdim["description"], \
                "Updating a dimension didn't work"


    def test_delete_dimension(self, client):
        # Add a new dimension and delete it

        # Test adding the object and deleting the name
        testdim = {'name':'Electric current'}
        client.add_dimension(wrap_item_into_dict("dimension", testdim))
        old_dimension_list = list(client.get_dimensions())

        client.delete_dimension(wrap_item_into_dict("dimension", testdim))

        new_dimension_list = list(client.get_dimensions())

        log.info(new_dimension_list)

        assert testdim["name"] in old_dimension_list and \
            testdim["name"] not in new_dimension_list, \
            "Deleting dimension didn't work."

        # Test adding the name and deleting by object
        # testdim = {'name':'Electric current'}
        # client.add_dimension(wrap_item_into_dict("dimension", testdim["name"]))
        # old_dimension_list = list(client.get_dimensions())
        #
        # client.delete_dimension(wrap_item_into_dict("dimension", json.dumps(testdim)))
        #
        # new_dimension_list = list(client.get_dimensions())
        #
        # log.info(new_dimension_list)
        #
        # assert testdim["name"] in old_dimension_list and \
        #     testdim["name"] not in new_dimension_list, \
        #     "Deleting dimension didn't work."

    def test_add_unit(self, client):
        # Add a new unit to an existing static dimension
        new_unit = JSONObject({})
        new_unit.name = 'Teaspoons per second'
        new_unit.abbr = 'tsp s^-1'
        new_unit.cf = 0               # Constant conversion factor
        new_unit.lf = 1.47867648e-05  # Linear conversion factor
        new_unit.dimension = 'Volumetric flow rate'
        new_unit.info = 'A flow of one tablespoon per second.'
        client.add_unit(wrap_item_into_dict("unit", new_unit))

        unitlist = list(client.get_units(wrap_item_into_dict("dimension", new_unit.dimension)))

        #log.info(unitlist)

        unitabbr = []
        for unit in unitlist:
            unitabbr.append(unit["abbr"])

        assert new_unit.abbr in unitabbr, \
            "Adding new unit didn't work."


        # Add a new unit to a custom dimension
        testdim = {'name':'Test dimension'}
        client.add_dimension(wrap_item_into_dict("dimension", testdim))

        testunit = JSONObject({})
        testunit.name = 'Test'
        testunit.abbr = 'ttt'
        testunit.cf = 21
        testunit.lf = 42
        testunit.dimension = testdim["name"]

        result = client.add_unit(wrap_item_into_dict("unit", testunit))


        unitlist = list(client.get_units(wrap_item_into_dict("dimension", testdim["name"])))
        #log.info(unitlist)
        assert len(unitlist) == 1, \
            "Adding a new unit didn't work as expected"

        assert unitlist[0]["name"] == 'Test', \
            "Adding a new unit didn't work as expected"

        client.delete_dimension(wrap_item_into_dict("dimension", testdim))



    def test_update_unit(self, client):
        # Add a new unit to a new dimension

        testdim = {'name':'Test dimension'}
        client.add_dimension(wrap_item_into_dict("dimension", testdim))

        testunit = JSONObject({})
        testunit.name = 'Test'
        testunit.abbr = 'ttt'
        testunit.cf = 21
        testunit.lf = 42
        testunit.dimension = testdim["name"]
        result = client.add_unit(wrap_item_into_dict("unit", testunit))

        # Update it
        testunit.cf = 0
        result = client.update_unit(wrap_item_into_dict("unit", testunit))

        unitlist = list(client.get_units(wrap_item_into_dict("dimension", testdim["name"])))

        assert len(unitlist) > 0 and int(unitlist[0]['cf']) == 0, \
            "Updating unit didn't work correctly."

        client.delete_dimension(wrap_item_into_dict("dimension", testdim))

    def test_delete_unit(self, client):
        # Add a new unit to a new dimension

        testdim = {'name':'Test dimension'}
        client.add_dimension(wrap_item_into_dict("dimension", testdim))

        testunit = JSONObject({})
        testunit.name = 'Test'
        testunit.abbr = 'ttt'
        testunit.cf = 21
        testunit.lf = 42
        testunit.dimension = testdim["name"]
        result = client.add_unit(wrap_item_into_dict("unit", testunit))

        # Check if the unit has been added
        unitlist = list(client.get_units(wrap_item_into_dict("dimension", testunit.dimension)))


        assert len(unitlist) > 0 and unitlist[0]['abbr'] == testunit.abbr, \
            "The adding has not worked properly"

        result = client.delete_unit(wrap_item_into_dict("unit", testunit))

        unitlist = list(client.get_units(wrap_item_into_dict("dimension", testunit.dimension)))

        assert len(unitlist) == 0, \
            "Deleting unit didn't work correctly."

        client.delete_dimension(wrap_item_into_dict("dimension", testdim))

    def test_convert_unit(self, client):
        result = client.convert_unit(
            {
                "value": "20",
                "unit1": 'm',
                "unit2": 'km'
            }
        )
        waited_results = [0.02]
        for i in range(len(result)):
            assert float(result[i]) == float(waited_results[i]),  \
                "Converting metres to kilometres didn't work."

        result = client.convert_unit(
            {
                "value": "20",
                "unit1": '2e6 m^3',
                "unit2": 'hm^3'
            }
        )
        waited_results = [40]
        for i in range(len(result)):
            assert float(result[i]) == float(waited_results[i]),  \
                "Unit conversion of array didn't work."


    def test_convert_units(self, client):
        result = client.convert_units(
            {
                "values": ["20.", '30.', '40.'],
                "unit1": 'm',
                "unit2": 'km'
            }
        )
        waited_results = [0.02, 0.03, 0.04]
        for i in range(len(result)):
            assert float(result[i]) == float(waited_results[i]),  \
                "Unit conversion of array didn't work."




    def test_check_consistency(self, client):
        result1 = client.check_consistency({
            "unit": 'm^3',
            "dimension": 'Volume'
        })
        assert result1 is True, \
            "Unit consistency check didn't work."

        result2 = client.check_consistency({
            "unit": 'm',
            "dimension": 'Volume'
        })
        # result2 = client.check_consistency('m', 'Volume')
        assert result2 is False, \
            "Unit consistency check didn't work."


    def test_is_global_dimension(self, client):
        result = client.is_global_dimension({"dimension":{'name': 'Length'}})
        assert result is True, \
            "Is global dimension check didn't work."

    def test_is_global_unit(self, client):
        # result = client.is_global_unit({"unit": json.dumps({'abbr':'m'})})
        result = client.is_global_unit({"unit": {'abbr':'m'}})
        assert result is True, \
            "Is global unit check didn't work."


    # Version coming from the old unitttests
    # def test_convert_dataset(self, client):
    #     network = self.create_network_with_data(num_nodes=2)
    #     scenario = \
    #         network.scenarios.Scenario[0].resourcescenarios.ResourceScenario
    #     # Select the first array (should have untis 'bar') and convert it
    #     for res_scen in scenario:
    #         if res_scen.value.type == 'array':
    #             dataset_id = res_scen.value.id
    #             old_val = res_scen.value.value
    #             break
    #     newid = self.client.service.convert_dataset(dataset_id, 'mmHg')
    #
    #     assert newid is not None
    #     assert newid != dataset_id, "Converting dataset not completed."
    #
    #     new_dataset = self.client.service.get_dataset(newid)
    #     new_val = new_dataset.value
    #
    #     new_val = arr_to_vector(json.loads(new_val))
    #     old_val = arr_to_vector(json.loads(old_val))
    #
    #     old_val_conv = [i * 100000 / 133.322 for i in old_val]
    #
    #     # Rounding is not exactly the same on the server, that's why we
    #     # calculate the sum.
    #     assert sum(new_val) - sum(old_val_conv) < 0.00001, \
    #         "Unit conversion did not work"

    # Version in hydra-base
    # def test_convert_dataset(self, client):
    #     project = util.create_project()
    #
    #     network = util.create_network_with_data(num_nodes=2, project_id=project.id)
    #
    #     scenario = \
    #         network.scenarios[0].resourcescenarios
    #
    #     # Select the first array (should have untis 'bar') and convert it
    #     for res_scen in scenario:
    #         if res_scen.value.type == 'array':
    #             dataset_id = res_scen.value.id
    #             old_val = res_scen.value.value
    #             break
    #     newid = client.convert_dataset(dataset_id, 'mmHg')
    #
    #     assert newid is not None
    #     assert newid != dataset_id, "Converting dataset not completed."
    #     log.info(newid)
    #
    #     new_dataset = client.get_dataset(newid)
    #     new_val = new_dataset.value
    #
    #     new_val = arr_to_vector(json.loads(new_val))
    #     old_val = arr_to_vector(json.loads(old_val))
    #
    #     old_val_conv = [i * 100000 / 133.322 for i in old_val]
    #
    #     # Rounding is not exactly the same on the server, that's why we
    #     # calculate the sum.
    #     assert sum(new_val) - sum(old_val_conv) < 0.00001, \
    #         "Unit conversion did not work"
    #

if __name__ == '__main__':
    server.run()
