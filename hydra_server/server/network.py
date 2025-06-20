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
from spyne.model.primitive import Unicode, Integer, AnyDict
from spyne.model.complex import Array as SpyneArray
from spyne.decorator import rpc
from .complexmodels import Network,\
    Node,\
    Link,\
    Scenario,\
    ResourceGroup,\
    NetworkExtents,\
    ResourceSummary,\
    ResourceAttr,\
    ResourceScenario,\
    ResourceData
import hydra_base as hb
from .service import HydraService
import datetime
import logging
import json
from hydra_base.lib.objects import JSONObject

log = logging.getLogger(__name__)

class NetworkService(HydraService):
    """
        The network SOAP service.
    """

    @rpc(AnyDict, _returns=AnyDict)
    def add_network(ctx, net):
        """
        Takes an entire network complex model and saves it to the DB.  This
        complex model includes links & scenarios (with resource data).  Returns
        the network's complex model.

        As links connect two nodes using the node_ids, if the nodes are new
        they will not yet have node_ids. In this case, use negative ids as
        temporary IDS until the node has been given an permanent ID.

        All inter-object referencing of new objects should be done using
        negative IDs in the client.

        The returned object will have positive IDS

        Args:
            net (complexmodels.Network): The entire network complex model structure including nodes, links, scenarios and data

        Returns:
            complexmodels.Network: The full network structure, with correct IDs for all resources

        """
        net = hb.network.add_network(JSONObject(net), **ctx.in_header.__dict__)
        log.info("Creating response Network")
        ret_net = ResourceSummary(net, include_attributes=False)
        log.info("Response Network Created")

        return JSONObject(ret_net)

    @rpc(Integer,
         Unicode(pattern="[YN]", default='N'), #include attributes
         Unicode(pattern="[YN]", default='Y'), #include data
         Unicode(pattern="[YN]", default='N'), #include results
         SpyneArray(Integer()), #scenario ids
         Integer(), #template id
         Unicode(pattern="[YN]", default='N'), #include non template attributes
         Unicode(pattern="[YN]", default='N'), #include metadata
         _returns=AnyDict)
    def get_network(ctx, network_id, include_attributes, include_data, include_results, scenario_ids, template_id, include_non_template_attributes, include_metadata):
        """
        Return a whole network as a complex model.

        Args:
            network_id (int)              : The ID of the network to retrieve
            include_attributes (char) ('Y' or 'N'): Optional flag to indicate whether attributes are returned with the nodes & links. Seting to 'Y' has significant speed improvements at the cost of not retrieving attribute information.
            include_data (char) ('Y' or 'N'): Optional flag to indicate whether to return datasets with the network. Defaults to 'N', as it is is much faster.
            include_results (char) ('Y' or 'N'): Optional flag to indicate whether to return result datasets with the network. Defaults to 'Y', but using 'N' is much faster.
            template_id  (int)              : Optional parameter which will only return attributes on the resources that are in this template.
            scenario_ids (List(int))        : Optional parameter to indicate which scenarios to return with the network. If left unspecified, all scenarios are returned
            include_non_template_attributes: Include attributes which are not associated to ANY template.
        Returns:
            complexmodels.Network: A network complex model

        Raises:
            ResourceNotFoundError: If the network is not found.
        """
        net  = hb.network.get_network(network_id,
                                      include_attributes in ('Y', None),
                                      include_data in ('Y', None),
                                      include_results in ('Y', None),
                                      scenario_ids,
                                      template_id,
                                      include_non_template_attributes == 'Y',
                                      include_metadata=include_metadata == 'Y',
                                      **ctx.in_header.__dict__)

        include_data = include_data in ('Y', None)
        include_attributes = include_attributes in ('Y', None)

        ret_net = JSONObject(net)

        return ret_net

    @rpc(Integer,#network id
         Integer(default=None), #recipient user id
         Unicode(default=None), # new network name
         Integer(default=None), #project id
         Unicode(default=None), # project name
         Unicode(pattern="[YN]", default='Y'), # new project
         Unicode(pattern="[YN]", default='Y'), # include outputs
         SpyneArray(Integer), # scenario ID to clone
         _returns=Integer())
    def clone_network(ctx,
                      network_id,
                      recipient_user_id=None,
                      new_network_name=None,
                      project_id=None,
                      project_name=None,
                      new_project=True,
                      include_outputs=False,
                      scenario_ids=[]):
        """
         Create an exact clone of the specified network for the specified user.

         If project_id is specified, put the new network in there.

         Otherwise create a new project with the specified name and put it in there.

        """

        newnetworkid = hb.network.clone_network(network_id,
                                             recipient_user_id=recipient_user_id,
                                             new_network_name=new_network_name,
                                             project_id=project_id,
                                             project_name=project_name,
                                             new_project=new_project == 'Y',
                                             include_outputs=include_outputs == 'Y',
                                             scenario_ids=[],
                                             **ctx.in_header.__dict__)

        return newnetworkid

    @rpc(Integer,
         _returns=Unicode)
    def get_network_as_json(ctx, network_id):
        """
        Return a whole network as a json string. Used for testing.

        Args:
            network_id (int): The ID of the network to retrieve

        Returns:
            string: A json-encoded representation of the network

        """
        net  = hb.network.get_network(network_id,
                                   False,
                                   True,
                                   [],
                                   None,
                                   **ctx.in_header.__dict__)

        return json.dumps(str(net))

    @rpc(Integer, Unicode, _returns=Network)
    def get_network_by_name(ctx, project_id, network_name):
        """
        Search for a network by its name and return it.

        Args:
            project_id (int): As network names are only unique within a project, search for the network within the specified project
            network_name (string): The name of the network

        Returns:
            complexmodels.Network: The entire network structure, no filtering is performed, so all data and attributes are returned

        Raises:
            ResourceNotFoundError: If the project or network is not found
        """

        net = hb.network.get_network_by_name(project_id, network_name, **ctx.in_header.__dict__)

        return Network(net)

    @rpc(Integer, Unicode, _returns=Unicode)
    def network_exists(ctx, project_id, network_name):
        """
        Using a network's name, check if a network exists or not within a project.

        Args:
            project_id (int): The project in which you are searching
            network_name (string): The name of the network you are searching for

        Returns:
           Unicode: 'Y' or 'N'

        Raises:
            ResourceNotFoundError: If the project is not defined
        """

        net_exists = hb.network.network_exists(project_id, network_name, **ctx.in_header.__dict__)

        return net_exists

    @rpc(Network,
         Unicode(pattern="['YN']", default='Y'),
         Unicode(pattern="['YN']", default='Y'),
         Unicode(pattern="['YN']", default='Y'),
         Unicode(pattern="['YN']", default='Y'),
        _returns=Network)
    def update_network(ctx, net, update_nodes, update_links, update_groups, update_scenarios):
        """
        Update an entire network.
        Send a network complex model with updated nodes, links, groups or scenarios. Using
        flags, tell the function which of these to update.

        Args:
            net (complexmodels.Network): A network reflecting an already existing
                                         network (must have an ID), which is to be updated
            updated_nodes (char) (Y or N): Flag to indicated whether the
                                           incoming network's nodes should be updated
            updated_links (char) (Y or N): Flag to indicated whether the
                                           incoming network's links should be updated
            updated_groups (char) (Y or N): Flag to indicated whether the
                                            incoming network's resource groups
                                            should be updated
            updated_scenarios (char) (Y or N): Flag to indicated whether the
                                               incoming network's data should be updated

        Returns:
            complexmodels.Network: The updated network,
                                   in summarised forms (without data or attributes)

        Raises:
            ResourceNotFoundError: If the network does not exist.


        """
        upd_nodes = update_nodes in ('Y', None)
        upd_links = update_links in ('Y', None)
        upd_groups = update_groups in ('Y', None)
        upd_scenarios = update_scenarios in ('Y', None)

        net = hb.network.update_network(net,
                                     upd_nodes,
                                     upd_links,
                                     upd_groups,
                                     upd_scenarios,
                                     **ctx.in_header.__dict__)

        return Network(net, include_attributes=False, include_data=True)

    @rpc(Integer, Integer(min_occurs=0), _returns=Node)
    def get_node(ctx, node_id, scenario_id):
        """
        Get a node using the node_id.
        optionally, scenario_id can be included if data is to be included

        Args:
            node_id (int): The node to retrieve
            scenario_id (int) (optional): Include this if you want to include data with the scenario

        Returns:
            complexmodels.Node: A node complex model, with attributes and data if requested)

        Raises:
            ResourceNotFoundError: If the node or scenario is not found

        """
        node = hb.network.get_node(node_id, **ctx.in_header.__dict__)

        if scenario_id is not None:
            ret_node = Node(node)

            res_scens =hb.scenario.get_resource_data('NODE', node_id, scenario_id, None)

            rs_dict = {}
            for rs in res_scens:
                rs_dict[rs.resource_attr_id] = rs

            for ra in ret_node.attributes:
                if rs_dict.get(ra.id):
                    ra.resourcescenario = ResourceScenario(rs_dict[ra.id])

            return ret_node
        else:
            ret_node = Node(node)
            return ret_node

    @rpc(Integer, Integer, _returns=Link)
    def get_link(ctx, link_id, scenario_id):
        """
        Get a link using the link_id.
        optionally, scenario_id can be included if data is to be included

        Args:
            link_id (int): The link to retrieve
            scenario_id (int) (optional): Include this if you want to include data with the scenario

        Returns:
            complexmodels.Link: A link complex model, with attributes and data if requested)

        Raises:
            ResourceNotFoundError: If the link or scenario is not found

        """
        link = hb.network.get_link(link_id, **ctx.in_header.__dict__)

        if scenario_id is not None:
            ret_link = Link(link)
            res_scens =hb.scenario.get_resource_data('LINK', link_id, scenario_id, None)
            rs_dict = {}
            for rs in res_scens:
                rs_dict[rs.resource_attr_id] = rs

            for ra in ret_link.attributes:
                if rs_dict.get(ra.id):
                    ra.resourcescenario = ResourceScenario(rs_dict[ra.id])

            return ret_link
        else:
            ret_link = Link(link)
            return ret_link

    @rpc(Integer, Integer, _returns=ResourceGroup)
    def get_resourcegroup(ctx, group_id, scenario_id):
        """
        Get a resourcegroup using the group_id.
        optionally, scenario_id can be included if data is to be included

        Args:
            group_id (int): The resource group to retrieve
            scenario_id (int) (optional): Include this if you want to include data with the scenario

        Returns:
            complexmodels.ResourceGroup: A resource group complex model, with attributes and data if requested)

        Raises:
            ResourceNotFoundError: If the group or scenario is not found

        """
        group = hb.network.get_resourcegroup(group_id, **ctx.in_header.__dict__)

        if scenario_id is not None:
            ret_group = ResourceGroup(group)
            res_scens =hb.scenario.get_resource_data('GROUP', group_id, scenario_id, None)
            rs_dict = {}
            for rs in res_scens:
                rs_dict[rs.resource_attr_id] = rs

            for ra in ret_group.attributes:
                if rs_dict.get(ra.id):
                    ra.resourcescenario = ResourceScenario(rs_dict[ra.id])

            return ret_group
        else:
            ret_group = ResourceGroup(group)
            return ret_group

    @rpc(Integer, Unicode(pattern='[XY]'), _returns=Unicode)
    def delete_network(ctx, network_id, purge_data):
        """
        Set status of network to 'X' so it will no longer appear when you retrieve its project.
        This will not delete the network from the DB. For that use purge_network

        Args:
            network_id (int): The network to delete
            purge_data (string) ('Y' or 'N'): Any data left unconnected can be left in the DB or deleted with this flag.

        Returns:
            string: 'OK'

        Raises:
            ResourceNotFoundError: If the network is not found
        """
        hb.network.delete_network(network_id, purge_data, **ctx.in_header.__dict__)
        return 'OK'

    @rpc(Integer, Unicode(pattern="[YN]", default='Y'), _returns=Unicode)
    def purge_network(ctx, network_id, purge_data):
        """
        Remove a network from hydra platform completely.

        Args:
            network_id (int): The network to remove completely
            purge_data (string) ('Y' or 'N'): Any data left unconnected can be left in the DB or deleted with this flag.

        Returns:
            string: 'OK'

        Raises:
            ResourceNotFoundError: If the network is not found
        """
        #check_perm('delete_network')
        hb.network.purge_network(network_id, purge_data, **ctx.in_header.__dict__)
        return 'OK'

    @rpc(Integer, Unicode(pattern="[AX]"),  _returns=Unicode)
    def set_network_status(ctx, network_id, status):
        """
        Set status of network to the specified status character

        Args:
            network_id (int): The network to delete
            status (char): A or X

        Returns:
            string: 'OK'

        Raises:
            ResourceNotFoundError: If the network is not found
        """

        #check_perm('edit_topology')
        hb.network.set_network_status(network_id, status.upper(), **ctx.in_header.__dict__)
        return 'OK'


    @rpc(Integer, _returns=Unicode)
    def activate_network(ctx, network_id):
        """
        Un-Deletes a network. (Set the status to 'Y' meaning it'll be included
        when you request a project's networks.

        Args:
            network_id (int): The network to reactivate

        Returns:
            string: 'OK'

        Raises:
            ResourceNotFoundError: If the network is not found.
        """
        #check_perm('delete_network')
        hb.network.set_network_status(network_id, 'A', **ctx.in_header.__dict__)
        return 'OK'

    @rpc(Integer, _returns=NetworkExtents)
    def get_network_extents(ctx, network_id):
        """
        Given a network, return its maximum extents.
        This would be the minimum x value of all nodes,
        the minimum y value of all nodes,
        the maximum x value of all nodes and
        maximum y value of all nodes.

        Args:
            network_id (int): The network to get the extents for

        Returns:
            NetworkExtents: the min x, max x, min y, max y of all nodes in the network

        Raises:
            ResourceNotFoundError: If the network is not found.

        """
        extents = hb.network.get_network_extents(network_id, **ctx.in_header.__dict__)

        ne = NetworkExtents()
        ne.network_id = extents['network_id']
        ne.min_x = extents['min_x']
        ne.max_x = extents['max_x']
        ne.min_y = extents['min_y']
        ne.max_y = extents['max_y']

        return ne

    @rpc(Integer, Node, _returns=Node)
    def add_node(ctx, network_id, node):

        """
        Add a node to a network:

        .. code-block:: python

            (Node){
               id = 1027
               name = "Node 1"
               description = "Node Description"
               x = 0.0
               y = 0.0
               attributes =
                  (ResourceAttrArray){
                     ResourceAttr[] =
                        (ResourceAttr){
                           attr_id = 1234
                        },
                        (ResourceAttr){
                           attr_id = 4321
                        },
                  }
             }

        Args:
            network_id (int):  The id of the network to receive the new node
            node       (complexmodels.Node): The node to be added (see above for the format)

        Returns:
            complexmodels.Node: The newly added node, complete with an ID

        Raises:
            ResourceNotFoundError: If the network is not found
        """

        node_dict = hb.network.add_node(network_id, node, **ctx.in_header.__dict__)

        new_node = Node(node_dict)

        return new_node


    @rpc(Integer,  SpyneArray(Node), _returns=SpyneArray(Node))
    def add_nodes(ctx, network_id, nodes):

        """
        Add a lost of nodes to a network

        Args:
            network_id (int):  The id of the network to receive the new node
            node       (List(complexmodels.Node)): A list of the nodes to be added

        Returns:
            List(complexmodels.Node): The newly added nodes, each complete with an ID

        Raises:
            ResourceNotFoundError: If the network is not found
        """

        node_s = hb.network.add_nodes(network_id, nodes, **ctx.in_header.__dict__)
        new_nodes=[]
        for node in nodes:
            for node_ in node_s:
                if(node.name==node_.node_name):
                    new_nodes.append(Node(node_, include_attributes=True))
                    break

        return new_nodes

    @rpc(Integer,  SpyneArray(Link), _returns=SpyneArray(Link))
    def add_links(ctx, network_id, links):

        """
        Add a lost of links to a network

        Args:
            network_id (int):  The id of the network to receive the new link
            link       (List(complexmodels.Link)): A list of the links to be added

        Returns:
            List(complexmodels.Link): The newly added links, each complete with an ID

        Raises:
            ResourceNotFoundError: If the network is not found

        """
        link_s = hb.network.add_links(network_id, links, **ctx.in_header.__dict__)

        new_links=[]
        for link in links:
            for link_ in link_s:
                if(link.name==link_.link_name):
                    new_links.append(Link(link_, include_attributes=True))
                    break

        return new_links


    @rpc(Node, _returns=Node)
    def update_node(ctx, node):
        """
        Update a node.
        If new attributes are present, they will be added to the node.
        The non-presence of attributes does not remove them.

        .. code-block:: python

            (Node){
               id = 1039
               name = "Node 1"
               description = "Node Description"
               x = 0.0
               y = 0.0
               status = "A"
               attributes =
                  (ResourceAttrArray){
                     ResourceAttr[] =
                        (ResourceAttr){
                           id = 850
                           attr_id = 1038
                           ref_id = 1039
                           ref_key = "NODE"
                           attr_is_var = True
                        },
                        (ResourceAttr){
                           id = 852
                           attr_id = 1040
                           ref_id = 1039
                           ref_key = "NODE"
                           attr_is_var = True
                        },
                  }
             }

        Args:
            node (complexmodels.Node): The node to be updated

        Returns:
            complexmodels.Node: The updated node.

        Raises:
            ResourceNotFoundError: If the node is not found
        """

        node_dict = hb.network.update_node(node, **ctx.in_header.__dict__)
        updated_node = Node(node_dict)

        return updated_node

    @rpc(Integer, Unicode, _returns=Unicode)
    def set_node_status(ctx, node_id, status):
        """
        Set status of node to the specified status character

        Args:
            node_id (int): The node to delete
            status (char): A or X

        Returns:
            string: 'OK'

        Raises:
            ResourceNotFoundError: If the node is not found
        """
        #check_perm('edit_topology')
        hb.network.set_node_status(node_id, status.upper(), **ctx.in_header.__dict__)
        return 'OK'


    @rpc(Integer, Unicode(pattern='[YN]'), _returns=Unicode)
    def delete_node(ctx, node_id, purge_data):
        """
        Delete a node

        Args:
            node_id (int): The node to delete
            purge_data (Y or N): Flag to indicate if the associated data should be removed too

        Returns:
            string: 'OK'

        Raises:
            ResourceNotFoundError: If the node is not found

        """
        hb.network.delete_node(node_id, purge_data, **ctx.in_header.__dict__)
        return 'OK'

    @rpc(Integer, _returns=Unicode)
    def activate_node(ctx, node_id):
        """
        Set the status of a node to 'A'

        Un-Deletes a node. (Set the status to 'Y' meaning it'll be included
        when you request a network.

        Args:
            node_id (int): The node to reactivate

        Returns:
            string: 'OK'

        Raises:
            ResourceNotFoundError: If the node is not found.
        """
        #check_perm('edit_topology')
        hb.network.set_node_status(node_id, 'A', **ctx.in_header.__dict__)
        return 'OK'

    @rpc(Integer, Unicode(pattern="[YN]", default='Y'), _returns=Unicode)
    def purge_node(ctx, node_id, purge_data):
        """
            Remove node from DB completely
            If there are attributes on the node, use purge_data to try to
            delete the data. If no other resources link to this data, it
            will be deleted.

        Args:
            node_id (int): The node to remove completely
            purge_data (string) ('Y' or 'N'): Any data left unconnected can be left in the DB or deleted with this flag.

        Returns:
            string: 'OK'

        Raises:
            ResourceNotFoundError: If the node is not found
        """
        hb.network.delete_node(node_id, purge_data, **ctx.in_header.__dict__)
        return 'OK'

    @rpc(Integer, Link, _returns=Link)
    def add_link(ctx, network_id, link):
        """
        Add a link to a network

        Args:
            network_id (int):  The id of the network to receive the new link
            link       (complexmodels.Link): The link to be added (see above for the format)

        Returns:
            complexmodels.Link: The newly added link, complete with an ID

        Raises:
            ResourceNotFoundError: If the network is not found
        """

        link_dict = hb.network.add_link(network_id, link, **ctx.in_header.__dict__)
        new_link = Link(link_dict)

        return new_link

    @rpc(Link, _returns=Link)
    def update_link(ctx, link):
        """
        Update a link.

        Args:
            link       (complexmodels.Link): The link to be updated

        Returns:
            complexmodels.Link: The updated link.

        Raises:
            ResourceNotFoundError: If the link is not found
        """
        link_dict = hb.network.update_link(link, **ctx.in_header.__dict__)
        updated_link = Link(link_dict)

        return updated_link

    @rpc(Integer, Unicode(pattern='[YN]'), _returns=Unicode)
    def delete_link(ctx, link_id, purge_data):
        """
        Delete a link

        Args:
            link_id (int): The link to delete
            purge_data (Y or N): Flag to indicate if the associated data should be removed too

        Returns:
            string: 'OK'

        Raises:
            ResourceNotFoundError: If the link is not found

        """
        hb.network.delete_link(link_id, purge_data, **ctx.in_header.__dict__)
        return 'OK'

    @rpc(Integer, Unicode(pattern='[AX]'), _returns=Unicode)
    def set_link_status(ctx, link_id, status_code):
        """
        Set the status of a link to 'A'

        Args:
            link_id (int): The link to reactivate
            status_code (A or X): The status code

        Returns:
            string: 'OK'

        Raises:
            ResourceNotFoundError: If the link is not found.

        """
        hb.network.set_link_status(link_id, status_code, **ctx.in_header.__dict__)
        return 'OK'

    @rpc(Integer, _returns=Unicode)
    def activate_link(ctx, link_id):
        """
        Set the status of a link to 'A'

        Args:
            link_id (int): The link to reactivate

        Returns:
            string: 'OK'

        Raises:
            ResourceNotFoundError: If the link is not found.

        """
        hb.network.set_link_status(link_id, 'A', **ctx.in_header.__dict__)
        return 'OK'

    @rpc(Integer, Unicode(pattern="[YN]", default='Y'), _returns=Unicode)
    def purge_link(ctx, link_id, purge_data):
        """
        Remove link from DB completely
        If there are attributes on the link, use purge_data to try to
        delete the data. If no other resources link to this data, it
        will be deleted.

        Args:
            link_id (int): The link to reactivate

        Returns:
            string: 'OK'

        Raises:
            ResourceNotFoundError: If the link is not found.
        """
        hb.network.delete_link(link_id, purge_data, **ctx.in_header.__dict__)
        return 'OK'

    @rpc(Integer, ResourceGroup, _returns=ResourceGroup)
    def add_group(ctx, network_id, group):
        """
        Add a resourcegroup to a network

        Args:
            network_id (int):  The id of the network to receive the new node
            group      (complexmodels.ResourceGroup): The group to be added

        Returns:
            complexmodels.ResourceGroup: The newly added group, complete with an ID

        Raises:
            ResourceNotFoundError: If the network is not found
        """

        group_i = hb.network.add_group(network_id, group, **ctx.in_header.__dict__)
        new_group = ResourceGroup(group_i)

        return new_group

    @rpc(Integer, Unicode(pattern="[YN]", default='Y'), _returns=Unicode)
    def delete_group(ctx, group_id, purge_data):
        """
        Set the status of a group to 'X'
        Args:
            group_id (int): The resource group to delete
            purge_data (string) ('Y' or 'N'): Any data left unconnected can be left in the DB or deleted with this flag.

        Returns:
            string: 'OK'

        Raises:
            ResourceNotFoundError: If the resource group is not found

        """
        hb.network.delete_group(group_id, purge_data, **ctx.in_header.__dict__)
        return 'OK'

    @rpc(Integer, Unicode(pattern="[YN]", default='Y'), _returns=Unicode)
    def purge_group(ctx, group_id, purge_data):
        """
        Remove a resource group from the DB completely. If purge data is set
        to 'Y', any data that is unconnected after the removal of the group
        will be removed also.

        Args:
            group_id (int): The resource group to remove completely
            purge_data (string) ('Y' or 'N'): Any data left unconnected can be left in the DB or deleted with this flag.

        Returns:
            string: 'OK'

        Raises:
            ResourceNotFoundError: If the resource group is not found

        """
        hb.network.delete_group(group_id, purge_data, **ctx.in_header.__dict__)
        return 'OK'

    @rpc(Integer, Unicode, _returns=Unicode)
    def set_group_status(ctx, group_id, status):
        """
        Set status of group to the specified status character

        Args:
            group_id (int): The group to delete
            status (char): A or X

        Returns:
            string: 'OK'

        Raises:
            ResourceNotFoundError: If the group is not found
        """
        #check_perm('edit_topology')
        hb.network.set_group_status(group_id, status.upper(), **ctx.in_header.__dict__)
        return 'OK'

    @rpc(Integer, _returns=Unicode)
    def activate_group(ctx, group_id):
        """
        Set the status of a group to 'A'

        Args:
            group_id (int): The resource group to reactivate

        Returns:
            string: 'OK'

        Raises:
            ResourceNotFoundError: If the resource group is not found.

        """
        hb.network.set_group_status(group_id, 'A', **ctx.in_header.__dict__)
        return 'OK'


    @rpc(Integer, _returns=SpyneArray(Scenario))
    def get_scenarios(ctx, network_id):
        """
        Get all the scenarios in a given network.

        Args:
            network_id (int): The network from which to retrieve the scenarios

        Returns:
            List(complexmodels.Scenario): All the scenarios in the network

        Raises:
            ResourceNotFoundError: If the network is not found
        """
        scenarios_i = hb.network.get_scenarios(network_id, **ctx.in_header.__dict__)

        scenarios = [Scenario(scen) for scen in scenarios_i]

        return scenarios

    @rpc(Integer, _returns=SpyneArray(Integer))
    def validate_network_topology(ctx, network_id):
        """
        Check for the presence of orphan nodes in a network.
        Args:
            network_id (int): The network to check

        Returns:
            List(int)): IDs of all the orphan nodes in the network

        Raises:
            ResourceNotFoundError: If the network is not found

        """
        return hb.network.validate_network_topology(network_id, **ctx.in_header.__dict__)

    @rpc(Integer, Integer, _returns=SpyneArray(ResourceSummary))
    def get_resources_of_type(ctx, network_id, type_id):
        """
        Return a list of Nodes, Links or ResourceGroups
        which have the specified type.

        Args:
            network_id (int): Types of resources in this network
            type_id    (int): Search for resources of this type.

        Returns:
            List(ResourceSummary): These objects contain the attributes common to all resources, namely: type, id, name, description, attribues and types.

        Raises:
            ResourceNotFoundError: If the network or type is not found
        """

        resources_of_type = hb.network.get_resources_of_type(network_id, type_id, **ctx.in_header.__dict__)

        return [ResourceSummary(r) for r in resources_of_type]

    @rpc(Integer, _returns=Unicode)
    def clean_up_network(ctx, network_id):
        """
        Purge all nodes, links, groups and scenarios from a network which
        have previously been deleted.

        Args:
            network_id (int): The network to clean up

        Returns:
            string: 'OK'

        Raises:
            ResourceNotFoundError: If the network is not found

        """
        return hb.network.clean_up_network(network_id, **ctx.in_header.__dict__)

    @rpc(Integer, #network id
         Integer, # scenario id
         Unicode, # resource type
         Integer(max_occurs="unbounded"), #'resource IDS
         Unicode(pattern="['YN']", default='N'), # include metadata
         _returns=SpyneArray(ResourceScenario))
    def get_attributes_for_resource(ctx, network_id, scenario_id, resource_type, resource_ids, include_metadata):
        """
        Return all the attributes for all the nodes in a given network and a
        given scenario.


        Args:
            network_id (int): The network to search in
            scenario_id (int): The scenario to search
            resource_type (string): NODE | LINK | GROUP
            node_ids (List(int)) (optional): The specific nodes to search for data in.
                                             If not specified, all the resources in
                                             the network will be searched.
            include_metadata: (string) ('Y' or 'N'): Default 'N'. Set to 'Y' to
                                                     return metadata. This may
                                                     vause a performance hit as
                                                     metadata is BIG!

        Returns:
            List(ResourceScenario)

        Raises:
            ResourceNotFoundError: If the network or scenario are not found

        """
        start = datetime.datetime.now()

        resourcescenarios = hb.network.get_attributes_for_resource(network_id,
                                                                scenario_id,
                                                                resource_type,
                                                                resource_ids,
                                                                include_metadata)

        log.info("Qry done in %s", (datetime.datetime.now() - start))
        start = datetime.datetime.now()

        return_rs = [ResourceScenario(rs, rs.resourceattr.attr_id) for rs in resourcescenarios]

        log.info("Return vals built in %s", (datetime.datetime.now() - start))

        return return_rs

    @rpc(Integer, Integer, Integer(max_occurs="unbounded"), Unicode(pattern="['YN']", default='N'), _returns=SpyneArray(ResourceAttr))
    def get_all_node_data(ctx, network_id, scenario_id, node_ids, include_metadata):
        """
        Return all the attributes for all the nodes in a given network and a
        given scenario.


        Args:
            network_id (int): The network to search in
            scenario_id (int): The scenario to search
            node_ids (List(int)) (optional): The specific nodes to search for data in. If not specified, all the nodes in the network will be searched.
            include_metadata: (string) ('Y' or 'N'): Default 'N'. Set to 'Y' to return metadata. This may vause a performance hit as metadata is BIG!

        Returns:
            List(ResourceAttr), each with a resourcescenario attribute, containing the actual value for the scenario specified.

        Raises:
            ResourceNotFoundError: If the network or scenario are not found

        """
        start = datetime.datetime.now()

        node_resourcescenarios = hb.network.get_attributes_for_resource(network_id, scenario_id, 'NODE', node_ids, include_metadata)

        log.info("Qry done in %s", (datetime.datetime.now() - start))
        start = datetime.datetime.now()

        return_ras = []
        for ns in node_resourcescenarios:
            ra = ResourceAttr(ns.resourceattr)
            x = ResourceScenario(ns, ra.attr_id)
            ra.resourcescenario = x
            return_ras.append(ra)

        log.info("Return vals built in %s", (datetime.datetime.now() - start))

        return return_ras

    @rpc(Integer, Unicode(pattern="['YN']", default='N'), Unicode(pattern="['YN']", default='N'), Integer(min_occurs=0, max_occurs=1), Integer(min_occurs=0, max_occurs=1), _returns=SpyneArray(ResourceData))
    def get_all_resource_data(ctx, scenario_id, include_values, include_metadata, page_start, page_end):
        """
        Return all the attributes for all the nodes in a given network and a
        given scenario.

        In this function array data and timeseries data are returned as JSON strings.

        If your data structure looks like:

        +----+----+-----+
        | H1 | H2 | H3  |
        +====+====+=====+
        | 1  | 10 | 100 |
        +----+----+-----+
        | 2  | 20 | 200 |
        +----+----+-----+
        | 3  | 30 | 300 |
        +----+----+-----+
        | 4  | 40 | 400 |
        +----+----+-----+

        Then hydra will provide the data in the following format:

        '{
            "H1" : {"0":1, "1":2, "3":3, "4":4},\n
            "H2"  : {"0":10, "1":20, "3":30, "4":40},\n
            "H3"  : {"0":100, "1":200, "3":300, "4":400}\n
        }'

        For a timeseries:

        +-------------------------+----+----+-----+
        | Time                    | H1 | H2 | H3  |
        +=========================+====+====+=====+
        | 2014/09/04 16:46:12:00  | 1  | 10 | 100 |
        +-------------------------+----+----+-----+
        | 2014/09/05 16:46:12:00  | 2  | 20 | 200 |
        +-------------------------+----+----+-----+
        | 2014/09/06 16:46:12:00  | 3  | 30 | 300 |
        +-------------------------+----+----+-----+
        | 2014/09/07 16:46:12:00  | 4  | 40 | 400 |
        +-------------------------+----+----+-----+

        Then hydra will provide the data in the following format:

        '{
            "H1" : {\n
                    "2014/09/04 16:46:12:00":1,\n
                    "2014/09/05 16:46:12:00":2,\n
                    "2014/09/06 16:46:12:00":3,\n
                    "2014/09/07 16:46:12:00":4},\n

            "H2" : {\n
                    "2014/09/04 16:46:12:00":10,\n
                    "2014/09/05 16:46:12:00":20,\n
                    "2014/09/06 16:46:12:00":30,\n
                    "2014/09/07 16:46:12:00":40},\n

            "H3" :  {\n
                     "2014/09/04 16:46:12:00":100,\n
                     "2014/09/05 16:46:12:00":200,\n
                     "2014/09/06 16:46:12:00":300,\n
                     "2014/09/07 16:46:12:00":400}\n
        }'


        Args:
            scenario_id (int): The scenario to search
            include_values (string) ('Y' or 'N'): Default 'N'. Set to 'Y' to return the values. This may vause a performance hit as values are BIG!
            include_metadata: (string) ('Y' or 'N'): Default 'N'. Set to 'Y' to return metadata. This may vause a performance hit as metadata is BIG!
            page_start (int): The start of the search results (allows you to contol the nuber of results)
            page_end (int): The end of the search results

        Returns:
            List(ResourceData): A list of objects describing datasets specifically designed for efficiency

        """
        start = datetime.datetime.now()

        log.info("Getting all resource data for scenario %s", scenario_id)
        node_resourcedata = hb.network.get_all_resource_data(scenario_id,
                                                          include_metadata=include_metadata,
                                                          page_start=page_start,
                                                          page_end=page_end)

        log.info("Qry done in %s", (datetime.datetime.now() - start))

        start = datetime.datetime.now()

        return_ras = []
        for nodeattr in node_resourcedata:
            ra = ResourceData(nodeattr, include_values)
            return_ras.append(ra)

        log.info("%s return data found in %s", len(return_ras), (datetime.datetime.now() - start))

        return return_ras

    @rpc(Integer, Integer, Integer(max_occurs="unbounded"), Unicode(pattern="['YN']", default='N'), _returns=SpyneArray(ResourceAttr))
    def get_all_link_data(ctx, network_id, scenario_id, link_ids, include_metadata):
        """
        Return all the attributes for all the links in a given network and a
        given scenario.
        Returns a list of ResourceAttr objects, each with a resourcescenario
        attribute, containing the actual value for the scenario specified.

        Args:
            network_id (int): The network to search in
            scenario_id (int): The scenario to search
            link_ids (List(int)) (optional): The specific links to search for data in. If not specified, all the links in the network will be searched.
            include_metadata: (string) ('Y' or 'N'): Default 'N'. Set to 'Y' to return metadata. This may vause a performance hit as metadata is BIG!

        Returns:
            List(ResourceAttr), each with a resourcescenario attribute, containing the actual value for the scenario specified.

        Raises:
            ResourceNotFoundError: If the network or scenario are not found


        """
        start = datetime.datetime.now()

        link_resourcescenarios = hb.network.get_attributes_for_resource(network_id, scenario_id, 'LINK', link_ids, include_metadata)

        log.info("Qry done in %s", (datetime.datetime.now() - start))
        start = datetime.datetime.now()

        return_ras = []
        for linkrs in link_resourcescenarios:
            ra = ResourceAttr(linkrs.resourceattr)
            ra.resourcescenario = ResourceScenario(linkrs, ra.attr_id)
            return_ras.append(ra)

        log.info("Return vals built in %s", (datetime.datetime.now() - start))

        return return_ras

    @rpc(Integer, Integer, Integer(max_occurs="unbounded"), Unicode(pattern="['YN']", default='N'), _returns=SpyneArray(ResourceAttr))
    def get_all_group_data(ctx, network_id, scenario_id, group_ids, include_metadata):
        """
        Return all the attributes for all the groups in a given network and a
        given scenario.
        Returns a list of ResourceAttr objects, each with a resourcescenario
        attribute, containing the actual value for the scenario specified.

        Args:
            network_id (int): The network to search in
            scenario_id (int): The scenario to search
            group_ids (List(int)) (optional): The specific resource groups to search for data in. If not specified, all the groups in the network will be searched.
            include_metadata: (string) ('Y' or 'N'): Default 'N'. Set to 'Y' to return metadata. This may vause a performance hit as metadata is BIG!

        Returns:
            List(ResourceAttr), each with a resourcescenario attribute, containing the actual value for the scenario specified.

        """

        group_resourcescenarios = hb.network.get_attributes_for_resource(network_id, scenario_id, 'GROUP', group_ids, include_metadata)
        return_ras = []
        for grouprs in group_resourcescenarios:
            ra = ResourceAttr(grouprs.resourceattr)
            ra.resourcescenario = ResourceScenario(grouprs, ra.attr_id)
            return_ras.append(ra)

        return return_ras

    @rpc(Integer, Integer, _returns=SpyneArray(ResourceAttr))
    def get_all_resource_attributes_in_network(ctx, attr_id, network_id):
        """
            Get all the resource attributes in a network, for a specified attribute ID
        """
        network_ras = hb.network.get_all_resource_attributes_in_network(attr_id, network_id, **ctx.in_header.__dict__)

        return [ResourceAttr(ra) for ra in network_ras]

    @rpc(Integer, Integer, Integer, Integer, _returns=Unicode)
    def apply_unit_to_network_rs(ctx, network_id, unit_id, attr_id, scenario_id=None, **kwargs):
        """
            Set the unit on all the datasets in a network which have the same attribue
            as the supplied resource_attr_id.
            args:
                network_id (int): The network in which to operate
                unit_id (int): The unit ID to set on the network's datasets
                attr_id (int): The attribute ID
                scenario_id (int) (optional): Supplied if only datasets in a
                                              specific scenario are to be affected
            returns:
                'OK'
            raises:
                ValidationError if the supplied unit is incompatible with the attribute's dimension
        """
        res = hb.network.apply_unit_to_network_rs(
            network_id,
            unit_id,
            attr_id,
            scenario_id=scenario_id,
            **ctx.in_header.__dict__)
        return 'OK'
