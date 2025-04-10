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
import time
from spyne.model.primitive import Integer, Integer32, Unicode, AnyDict
from spyne.model.complex import Array as SpyneArray
from spyne.decorator import rpc
from .complexmodels import Scenario,\
        ResourceScenario,\
        Dataset,\
        ResourceAttr,\
        AttributeData,\
        ResourceGroupItem,\
        ScenarioDiff

import logging
log = logging.getLogger(__name__)
from hydra_base.lib import scenario
from .service import HydraService
from hydra_base.lib.objects import JSONObject

class ScenarioService(HydraService):
    """
        The scenario SOAP service
        as all resources already exist, there is no need to worry
        about negative IDS
    """

    @rpc(Integer,
         Unicode(pattern="['YN']", default='N'),
         Unicode(pattern="['YN']", default='N'),
         Unicode(pattern="['YN']", default='N'),
         Unicode(pattern="['YN']", default='N'),
         _returns=AnyDict)
    def get_scenario(ctx, scenario_id, get_parent_data, include_data, include_group_items, include_results):
        """
            Get the specified scenario
        """

        if get_parent_data is None or get_parent_data.upper() == 'N':
            _get_parent_data = False
        else:
            _get_parent_data = True

        if include_data is None or include_data.upper() == 'Y':
            _include_data = True
        else:
            _include_data = False

        if include_group_items is None or include_group_items.upper() == 'Y':
            _include_group_items = True
        else:
            _include_group_items = False

        if include_results is None or include_results.upper() == 'Y':
            _include_results = True
        else:
            _include_results = False

        t = time.time()

        scen = scenario.get_scenario(scenario_id,
                                     get_parent_data=_get_parent_data,
                                     include_data=_include_data,
                                     include_group_items=_include_group_items,
                                     include_results=_include_results,
                                     **ctx.in_header.__dict__)
        log.info('get_scenario took %s seconds' % (time.time() - t))
        return JSONObject(scen)

    @rpc(Integer,
         Unicode,
         Unicode(pattern="['YN']", default='N'),
         Unicode(pattern="['YN']", default='N'),
         Unicode(pattern="['YN']", default='N'),
         _returns=Scenario)
    def get_scenario_by_name(ctx, network_id, scenario_name, get_parent_data, include_data, include_group_items):
        """
            Get the specified scenario
        """
        if get_parent_data is None or get_parent_data.upper() == 'N':
            _get_parent_data = False
        else:
            _get_parent_data = True

        if include_data is None or include_data.upper() == 'Y':
            _include_data = True
        else:
            _include_data = False

        if include_group_items is None or include_group_items.upper() == 'Y':
            _include_group_items = True
        else:
            _include_group_items = False

        scen = scenario.get_scenario_by_name(network_id,
                                             scenario_name,
                                             get_parent_data=_get_parent_data,
                                             include_data=_include_data,
                                             include_group_items=_include_group_items,
                                             **ctx.in_header.__dict__)

        return Scenario(scen,
                        include_data=_include_data,
                        include_group_items=_include_group_items)

    @rpc(Integer, Scenario, Unicode(pattern="['YN']", default='N'), _returns=Scenario)
    def add_scenario(ctx, network_id, scen, return_summary):
        """
            Add a scenario to a specified network.
        """
        if return_summary is None:
            return_summary = 'N'
        _return_summary = return_summary.upper() == 'Y'

        new_scen = scenario.add_scenario(network_id, scen, **ctx.in_header.__dict__)

        return Scenario(new_scen,
                        include_data=not _return_summary,
                        include_group_items=not _return_summary)

    @rpc(AnyDict,
         Unicode(pattern="['YN']", default='Y'),
         Unicode(pattern="['YN']", default='Y'),
         Unicode(pattern="['YN']", default='N'), _returns=AnyDict)
    def update_scenario(ctx, scen, update_data, update_groups, return_summary):
        """
            Update a single scenario
            as all resources already exist, there is no need to worry
            about negative IDS
        """
        scen = JSONObject(scen)
        upd_data = update_data in ('Y', None)
        upd_grp  = update_groups in ('Y', None)

        if return_summary is None:
            return_summary = 'N'
        _return_summary = return_summary.upper() == 'Y'

        updated_scen = scenario.update_scenario(scen,
                                                update_data=upd_data,
                                                update_groups=upd_grp,
                                                **ctx.in_header.__dict__)

        returndict = {}
        for col in [c.name for c in updated_scen.__table__.columns]:
            returndict[col] = getattr(updated_scen, col)
        return JSONObject(returndict)

    @rpc(Integer, _returns=Unicode)
    def purge_scenario(ctx, scenario_id):
        """
            Set the status of a scenario to 'X'.
        """

        return scenario.purge_scenario(scenario_id, **ctx.in_header.__dict__)

    @rpc(Integer, Unicode(pattern="['AX']"), _returns=Unicode)
    def set_scenario_status(ctx, scenario_id, status):
        """
            Set the status of a scenario to 'A' or 'X'.
        """

        return scenario.set_scenario_status(scenario_id, status, **ctx.in_header.__dict__)

    @rpc(Integer, _returns=Unicode)
    def delete_scenario(ctx, scenario_id):
        """
            Set the status of a scenario to 'X'.
        """

        return scenario.set_scenario_status(scenario_id, 'X', **ctx.in_header.__dict__)

    @rpc(Integer, _returns=Unicode)
    def activate_scenario(ctx, scenario_id):
        """
            Set the status of a scenario to 'X'.
        """

        return scenario.set_scenario_status(scenario_id, 'A', **ctx.in_header.__dict__)


    @rpc(Integer,
         Unicode(pattern='[YN]'),
         Unicode,
         _returns=Scenario)
    def clone_scenario(ctx, scenario_id, retain_results, scenario_name):

        cloned_scen = scenario.clone_scenario(scenario_id,
                                              retain_results == 'Y',
                                              scenario_name,
                                              **ctx.in_header.__dict__)

        return Scenario(cloned_scen, include_data=False, include_group_items=False)

    @rpc(Integer, Unicode(default=None), _returns=Scenario)
    def create_child_scenario(ctx, scenario_id, child_name):
        """
            Create a new scenario which inherits from the specified scenario
        """
        child_scen = scenario.create_child_scenario(scenario_id, child_name, **ctx.in_header.__dict__)

        return Scenario(child_scen,
                        include_data=False,
                        include_group_items=False)

    @rpc(Integer, Integer, _returns=ScenarioDiff)
    def compare_scenarios(ctx, scenario_id_1, scenario_id_2):
        scenariodiff = scenario.compare_scenarios(scenario_id_1,
                                                  scenario_id_2,
                                                  **ctx.in_header.__dict__)

        return ScenarioDiff(scenariodiff)


    @rpc(Integer, _returns=Unicode)
    def lock_scenario(ctx, scenario_id):
        result = scenario.lock_scenario(scenario_id, **ctx.in_header.__dict__)
        return result

    @rpc(Integer, _returns=Unicode)
    def unlock_scenario(ctx, scenario_id):
        result = scenario.unlock_scenario(scenario_id, **ctx.in_header.__dict__)
        return result

    @rpc(Integer, _returns=SpyneArray(Scenario))
    def get_dataset_scenarios(ctx, dataset_id):
        """
            Get all the scenarios attached to a dataset
            @returns a list of scenario_ids
        """

        scenarios = scenario.get_dataset_scenarios(dataset_id, **ctx.in_header.__dict__)

        return [Scenario(s, include_data=False, include_group_items=False) for s in scenarios]

    @rpc(Integer, SpyneArray(ResourceScenario), _returns=SpyneArray(ResourceScenario))
    def update_resourcedata(ctx,scenario_id, resource_scenarios):
        """
            Update the data associated with a scenario.
            Data missing from the resource scenario will not be removed
            from the scenario. Use the remove_resourcedata for this task.
        """
        res = scenario.update_resourcedata(scenario_id,
                                           resource_scenarios,
                                           **ctx.in_header.__dict__)
        ret = [ResourceScenario(r) for r in res]
        return ret

    @rpc(SpyneArray(Integer32), SpyneArray(AnyDict), _returns=Unicode)
    def bulk_update_resourcedata(ctx, scenario_ids, resource_scenarios):
        """
            Update the data associated with a scenario.
            Data missing from the resource scenario will not be removed
            from the scenario. Use the remove_resourcedata for this task.
        """

        scenario.bulk_update_resourcedata(scenario_ids,
                                          [JSONObject(rs) for rs in resource_scenarios],
                                         **ctx.in_header.__dict__)

        return 'OK'

    @rpc(Integer, ResourceScenario, _returns=Unicode)
    def delete_resourcedata(ctx,scenario_id, resource_scenario):
        """
            Remove the data associated with a resource in a scenario.
        """
        success = 'OK'
        scenario.delete_resourcedata(scenario_id,
                                         resource_scenario,
                                         **ctx.in_header.__dict__)
        return success

    @rpc(Integer, Integer, Dataset, _returns=ResourceScenario)
    def add_data_to_attribute(ctx, scenario_id, resource_attr_id, dataset):
        """
                Add data to a resource scenario outside of a network update
        """
        new_rs = scenario.add_data_to_attribute(scenario_id,
                                                  resource_attr_id,
                                                  dataset,
                                                  **ctx.in_header.__dict__)
        x = ResourceScenario(new_rs)
        return x

    @rpc(Integer,
         Unicode(pattern="['YN']", default='N'),
         _returns=SpyneArray(Dataset))
    def get_scenario_data(ctx, scenario_id, get_parent_data):
        if get_parent_data is None:
            get_parent_data = 'N'

        scenario_data = scenario.get_scenario_data(scenario_id,
                                                   get_parent_data = True if get_parent_data == 'Y' else False,
                                                   **ctx.in_header.__dict__)
        data_cm = [Dataset(d) for d in scenario_data]
        return data_cm


    @rpc(Unicode,
         Integer,
         Integer,
         Integer(min_occurs=0, max_occurs=1),
         Unicode(pattern="['YN']", default='N'),
         _returns=SpyneArray(ResourceScenario))
    def get_resource_data(ctx, resource_type, resource_id, scenario_id, type_id=None, get_parent_data='N'):
        """
            Get all the resource scenarios for a given resource
            in a given scenario. If type_id is specified, only
            return the resource scenarios for the attributes
            within the type.
        """
        if get_parent_data is None or get_parent_data.upper() != 'Y':
            get_parent_data = False
        else:
            get_parent_data = True

        resource_data = scenario.get_resource_data(resource_type,
                                               resource_id,
                                               scenario_id,
                                               type_id,
                                               get_parent_data=get_parent_data,
                                               **ctx.in_header.__dict__
                                              )

        ret_data = [ResourceScenario(rs) for rs in resource_data]
        return ret_data


    @rpc(Integer,
         Integer,
         Integer(min_occurs=0, max_occurs=1),
         Unicode(pattern="['YN']", default='N'),
         _returns=SpyneArray(ResourceScenario))
    def get_node_data(ctx, node_id, scenario_id, type_id, get_parent_data):
        """
            Get all the resource scenarios for a given node
            in a given scenario. If type_id is specified, only
            return the resource scenarios for the attributes
            within the type.
        """
        node_data = scenario.get_resource_data('NODE',
                                               node_id,
                                               scenario_id,
                                               type_id,
                                               get_parent_data = True if get_parent_data == 'Y' else False,
                                               **ctx.in_header.__dict__
                                              )

        ret_data = [ResourceScenario(rs) for rs in node_data]
        return ret_data

    @rpc(Integer,
         Integer,
         Integer(min_occurs=0, max_occurs=1),
         Unicode(pattern="['YN']", default='N'),
         _returns=SpyneArray(ResourceScenario))
    def get_link_data(ctx, link_id, scenario_id, type_id, get_parent_data):
        """
            Get all the resource scenarios for a given link
            in a given scenario. If type_id is specified, only
            return the resource scenarios for the attributes
            within the type.
        """
        link_data = scenario.get_resource_data('LINK',
                                               link_id,
                                               scenario_id,
                                               type_id,
                                               get_parent_data = True if get_parent_data == 'Y' else False,
                                               **ctx.in_header.__dict__
        )

        ret_data = [ResourceScenario(rs) for rs in link_data]
        return ret_data

    @rpc(Integer,
         Integer,
         Integer(min_occurs=0, max_occurs=1),
         Unicode(pattern="['YN']", default='N'),
         _returns=SpyneArray(ResourceScenario))
    def get_network_data(ctx, network_id, scenario_id, type_id, get_parent_data):
        """
            Get all the resource scenarios for a given network
            in a given scenario. If type_id is specified, only
            return the resource scenarios for the attributes
            within the type.
        """
        network_data = scenario.get_resource_data('NETWORK',
                                               network_id,
                                               scenario_id,
                                               type_id,
                                               get_parent_data = True if get_parent_data == 'Y' else False,
                                                **ctx.in_header.__dict__)

        ret_data = [ResourceScenario(rs) for rs in network_data]
        return ret_data

    @rpc(Integer,
         Integer,
         Integer(min_occurs=0, max_occurs=1),
         Unicode(pattern="['YN']", default='N'),
         _returns=SpyneArray(ResourceScenario))
    def get_resourcegroup_data(ctx, resourcegroup_id, scenario_id, type_id, get_parent_data):
        """
            Get all the resource scenarios for a given resourcegroup
            in a given scenario. If type_id is specified, only
            return the resource scenarios for the attributes
            within the type.
        """
        group_data = scenario.get_resource_data('GROUP',
                                               resourcegroup_id,
                                               scenario_id,
                                               type_id,
                                               get_parent_data = True if get_parent_data == 'Y' else False,
                                               **ctx.in_header.__dict__)

        ret_data = [ResourceScenario(rs) for rs in group_data]
        return ret_data

    @rpc(SpyneArray(Integer), SpyneArray(Integer), _returns=AttributeData)
    def get_node_attribute_data(ctx, node_ids, attr_ids):
        """
            Get the data for multiple attributes on multiple nodes
            across multiple scenarios.
            @returns a list of AttributeData objects, which consist of a list
            of ResourceAttribute objects and a list of corresponding
            ResourceScenario objects.
        """

        node_attrs, resource_scenarios = scenario.get_attribute_data(attr_ids,
                                                                     node_ids,
                                                                    **ctx.in_header.__dict__)

        node_ras = [ResourceAttr(na) for na in node_attrs]
        node_rs  = [ResourceScenario(rs) for rs in resource_scenarios]

        ret_obj = AttributeData()
        ret_obj.resourceattrs = node_ras
        ret_obj.resourcescenarios = node_rs

        return ret_obj

    @rpc(Integer,
         Integer,
         Unicode(pattern="['YN']", default='N'), _returns=SpyneArray(ResourceScenario))
    def get_attribute_datasets(ctx, attr_id, scenario_id, get_parent_data):
        """
            Get all the datasets from resource attributes with the given attribute
            ID in the given scenario.

            Return a list of resource attributes with their associated
            resource scenarios (and values).
        """
        resource_scenarios = scenario.get_attribute_datasets(attr_id,
                                                             scenario_id,
                                                             get_parent_data = True if get_parent_data == 'Y' else False,
                                                             **ctx.in_header.__dict__)

        return [ResourceScenario(rs) for rs in resource_scenarios]

    @rpc(Integer(min_occurs=1, max_occurs='unbounded'), Integer, Integer, _returns=SpyneArray(ResourceScenario))
    def copy_data_from_scenario(ctx, resource_attr_ids, source_scenario_id, target_scenario_id):
        """
            Copy the datasets from a source scenario into the equivalent resource scenarios
            in the target scenario. Parameters are a list of resource attribute IDS, the
            ID of the source scenario and the ID of the target scenario.
        """
        updated_resourcescenarios = scenario.copy_data_from_scenario(resource_attr_ids,
                                                                     source_scenario_id,
                                                                     target_scenario_id,
                                                                     **ctx.in_header.__dict__)

        ret_resourcescenarios = [ResourceScenario(rs) for rs in updated_resourcescenarios]

        return ret_resourcescenarios

    @rpc(Integer, Integer, Integer, _returns=ResourceScenario)
    def set_rs_dataset(ctx, resource_attr_id, scenario_id, dataset_id):
        """
            A short-hand way of creating a resource scenario. This function says:
            assign this datset ID to this resource attribute in this scenario.
            All the IDs must already exist.
        """

        rs = scenario.set_rs_dataset(resource_attr_id,
                                     scenario_id,
                                     dataset_id,
                                     **ctx.in_header.__dict__)

        return ResourceScenario(rs)

    @rpc(Integer,
         Integer,
         Unicode(pattern="['YN']", default='N'),
         _returns=SpyneArray(ResourceGroupItem))
    def get_resourcegroupitems(ctx, group_id, scenario_id, get_parent_items):
        items = scenario.get_resourcegroupitems(group_id,
                                                scenario_id,
                                                get_parent_items = get_parent_items == 'Y',
                                                **ctx.in_header.__dict__)

        return [ResourceGroupItem(rgi) for rgi in items]

    @rpc(Integer, Integer, Integer, Integer, _returns=ResourceScenario)
    def update_value_from_mapping(ctx, source_resource_attr_id,
                                  target_resource_attr_id,
                                  source_scenario_id,
                                  target_scenario_id):

        updated_rs = scenario.update_value_from_mapping(
                                        source_resource_attr_id,
                                        target_resource_attr_id,
                                        source_scenario_id,
                                        target_scenario_id,
                                        **ctx.in_header.__dict__)

        if updated_rs is not None:
            return ResourceScenario(updated_rs)
        else:
            return None


    @rpc(Integer,
         Integer,
         Unicode(pattern="['YN']", default='N'),
         _returns=ResourceScenario)
    def get_resource_scenario(ctx, resource_attr_id, scenario_id, get_parent_data):
        """
            Get the resource scenario object for a given resource atttribute and scenario.
            This is done when you know the attribute, resource and scenario and want to get the
            value associated with it.

            The get_parent_data flag indicates whether we should look only at this scenario, or if
            the resource scenario does not exist on this scenario to look in its parent.

        """
        rs = scenario.get_resource_scenario(resource_attr_id,
                                            scenario_id,
                                            get_parent_data = True if get_parent_data == 'Y' else False,
                                            **ctx.in_header.__dict__)

        return ResourceScenario(rs)
    @rpc(Integer,
         SpyneArray(Integer),
         Unicode(pattern="['YN']", default='N'),
         _returns=Unicode)
    def delete_resource_scenarios(ctx, scenario_id, resource_attr_ids, quiet):
        """
            Delete a list of resoruce attributes associated to a scenario
        """
        scenario.delete_resource_scenarios(scenario_id,
                                           resource_attr_ids,
                                           quiet=quiet=='Y',
                                           **ctx.in_header.__dict__)
        return 'OK'

    @rpc(Integer,
         Integer,
         Unicode(pattern="['YN']", default='N'),
         _returns=Unicode)
    def delete_resource_scenario(ctx, scenario_id, resource_attr_id, quiet):
        """
            Delete a list of resoruce attributes associated to a scenario
        """
        scenario.delete_resource_scenario(scenario_id,
                                          resource_attr_id,
                                          quiet=quiet=='Y',
                                          **ctx.in_header.__dict__)
        return 'OK'
