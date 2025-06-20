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
from spyne.model.primitive import Integer, Unicode
from spyne.model.complex import Array as SpyneArray
from spyne.model.primitive import AnyDict
from spyne.decorator import rpc
from .complexmodels import Attr
from .complexmodels import ResourceAttr
from .complexmodels import ResourceAttrMap
from .complexmodels import AttrGroup
from .complexmodels import AttrGroupItem

from .service import HydraService

from hydra_base.lib import attributes
from hydra_base.lib.objects import JSONObject

import logging
log = logging.getLogger(__name__)

class AttributeService(HydraService):
    """
        The attribute SOAP service
    """
    @rpc(Attr, _returns=Attr)
    def add_attribute_no_checks(ctx, attr):
        """
        Add a generic attribute, which can then be used in creating
        a resource attribute, and put into a type.
        ***NO VALIDATION IS PERFORMED WHEN ADDING THIS ATTRIBUTE WHICH CAN
        LEAD TO DATABASE INCONSISTENCIES***

        .. code-block:: python

            (Attr){
                name = "Test Attr"
                dimen = "very big"
                description = "I am a very big attribute"
            }

        Args:
            attr (complexmodels.Attr): An attribute object, as described above.

        Returns:
            complexmodels.Attr: An attribute object, similar to the one sent in but with an ID.
        """

        attr = attributes.add_attribute_no_checks(attr, **ctx.in_header.__dict__)
        return Attr(attr)

    @rpc(Attr, _returns=Attr)
    def add_attribute(ctx, attr):
        """
        Add a generic attribute, which can then be used in creating
        a resource attribute, and put into a type.

        .. code-block:: python

            (Attr){
                name = "Test Attr"
                dimen = "very big"
                description = "I am a very big attribute"
            }

        Args:
            attr (complexmodels.Attr): An attribute object, as described above.

        Returns:
            complexmodels.Attr: An attribute object, similar to the one sent in but with an ID.
        """

        attr = attributes.add_attribute(attr, **ctx.in_header.__dict__)
        return Attr(attr)

    @rpc(Attr, _returns=Attr)
    def add_attribute_no_checks(ctx, attr):
        """
        ***WARNING*** This is used for test purposes only, and can allow
        duplicate attributes to be created
        """
        log.debug("Adding attribute: %s", attr.name)
        attr = attributes.add_attribute_no_checks(attr, **ctx.in_header.__dict__)
        return Attr(attr)

    @rpc(Attr, _returns=Attr)
    def update_attribute(ctx, attr):
        """
        Update a generic attribute, which can then be used in creating a resource attribute, and put into a type.

        .. code-block:: python

            (Attr){
                id = 1020
                name = "Test Attr"
                dimen = "very big"
                description = "I am a very big attribute"
            }

        Args:
            attr (complexmodels.Attr): An attribute complex model, as described above.

        Returns:
            complexmodels.Attr: An attribute complex model, reflecting the one sent in.

        """
        attr = attributes.update_attribute(attr, **ctx.in_header.__dict__)
        return Attr(attr)

    @rpc(Integer, _returns=Unicode)
    def delete_attribute(ctx, attr_id):
        """
        Delete an attribute

        Args:
            attr_id (int): The ID of the attribute

        Returns:
            string: 'OK' if all is well. If the mapping isn't there, it'll still return 'OK', so make sure the IDs are correct!

        """
        attributes.delete_attribute(attr_id, **ctx.in_header.__dict__)

        return 'OK'

    @rpc(SpyneArray(Attr), _returns=SpyneArray(Attr))
    def add_attributes(ctx, attrs):
        """
        Add multiple generic attributes

        Args:
            attrs (List[Attr]): A list of attribute complex models,
                as described above.

        Returns:
            List[Attr]: A list of attribute complex models,
                reflecting the ones sent in.

        """

        attrs = attributes.add_attributes(attrs, **ctx.in_header.__dict__)
        ret_attrs = [Attr(attr) for attr in attrs]
        return ret_attrs

    @rpc(_returns=SpyneArray(Attr))
    def get_all_attributes(ctx):
        """
        Get all the attributes in the system

        Args:
            None

        Returns:
            List[Attr]: A list of attribute complex models
        """

        attrs = attributes.get_attributes(**ctx.in_header.__dict__)
        ret_attrs = [Attr(attr) for attr in attrs]
        return ret_attrs

    @rpc(Integer, _returns=Attr)
    def get_attribute_by_id(ctx, attr_id):
        """
        Get a specific attribute by its ID.

        Args:
            attr_id (int): The ID of the attribute

        Returns:
            complexmodels.Attr: An attribute complex model.
                Returns None if no attribute is found.
        """
        attr = attributes.get_attribute_by_id(attr_id, **ctx.in_header.__dict__)

        return Attr(attr)

    @rpc(SpyneArray(Integer), _returns=SpyneArray(Attr))
    def get_attributes_by_id(ctx, attr_ids):
        """
        Get a list of specified attributes by their ID.

        Args:
            attr_ids (list(int)): The list of IDs of the attribute

        Returns:
            list(complexmodels.Attr): An attribute complex model.
                Returns [] if no attribute is found.
        """
        attrs = attributes.get_attributes_by_id(attr_ids, **ctx.in_header.__dict__)

        return [Attr(attr) for attr in attrs]

    @rpc(Unicode, Integer, _returns=Attr)
    def get_attribute_by_name_and_dimension(ctx, name, dimension_id):
        """
        Get a specific attribute by its name and dimension (this combination
        is unique for attributes in Hydra Platform).

        Args:
            name (unicode): The name of the attribute
            dimension (unicode): The dimension of the attribute

        Returns:
            complexmodels.Attr: An attribute complex model.
                Returns None if no attribute is found.

        """
        attr = attributes.get_attribute_by_name_and_dimension(name,
                                                              dimension_id,
                                                              **ctx.in_header.__dict__)
        if attr:
            return Attr(attr)

        return None

    @rpc(Integer, _returns=SpyneArray(Attr))
    def get_template_attributes(ctx, template_id):
        """
            Get all the attributes in a template.
            Args

                param (int) template_id

            Returns

                List(Attr)
        """
        attrs = attributes.get_template_attributes(template_id,**ctx.in_header.__dict__)

        return [Attr(a) for a in attrs]

    @rpc(Integer(default=None), Integer(default=None), Unicode(pattern="['YN']", default='N'), Unicode(pattern="['YN']", default='N'), _returns=SpyneArray(AnyDict))
    def get_attributes(ctx, network_id, project_id, include_global, include_hierarchy):
        """
        Get all attributes

        Args:
            network_id: Include any attributes scoped to this network
            project_id: Include any attribute scoped to this project
            include_global: Include un-scoped attributes (Note this can return a LOT of attributes, and affect performance.)
            include_hierarchy: Include attributes defined on the parent projects to the specified project

        Returns:
            List(AnyDict): List of Dicts

        """

        include_global = include_global == 'Y'
        include_hierarchy = include_hierarchy == 'Y'

        attrs = attributes.get_attributes(network_id=network_id,
                                          project_id=project_id,
                                          include_global=include_global,
                                          include_hierarchy=include_hierarchy)

        return [JSONObject(a) for a in attrs]

    @rpc(Unicode, Integer, Integer, Unicode(pattern="['YN']", default='N'), _returns=ResourceAttr)
    def add_resource_attribute(ctx,resource_type, resource_id, attr_id, is_var):
        """
        Add a resource attribute to a node.

        Args:
            resource_type (string) : NODE | LINK | GROUP | NETWORK
            resource_id (int): The ID of the Node
            attr_id (int): The ID if the attribute being added.
            is_var (char): Y or N. Indicates whether the attribute is a variable or not.

        Returns:
            complexmodels.ResourceAttr: The newly created node attribute

        Raises:
            ResourceNotFoundError: If the node or attribute do not exist
            HydraError: If this addition causes a duplicate attribute on the node.

        """
        new_ra = attributes.add_resource_attribute(
            resource_type,
            resource_id,
            attr_id,
            is_var,
            **ctx.in_header.__dict__)

        return ResourceAttr(new_ra)

    @rpc(SpyneArray(AnyDict), _returns=SpyneArray(Integer))
    def add_resource_attributes(ctx,resource_attributes):
        """
        Add a resource attribute to a node.

        Args:
            A list of dicts containing:
                resource_type (string) : NODE | LINK | GROUP | NETWORK
                resource_id (int): The ID of the Node
                attr_id (int): The ID if the attribute being added.
                is_var (char): Y or N. Indicates whether the attribute is a variable or not.
                error_on_duplicate: Y or N: Indicates whether to throw an error on finding a duplciate attribute on the resource, or just ignoring it.

        Returns:
            SpyneArray(Integer): The IDs of the newly created node attributes

        Raises:
            ResourceNotFoundError: If the node or attribute do not exist
            HydraError: If this addition causes a duplicate attribute on the node.

        """
        new_ids = attributes.add_resource_attributes([JSONObject(ra) for ra in resource_attributes], **ctx.in_header.__dict__)

        return new_ids

    @rpc(Integer, Unicode(pattern="['YN']"), _returns=ResourceAttr)
    def update_resource_attribute(ctx, resource_attr_id, is_var):
        """
        Update a resource attribute (which means update the is_var flag
        as this is the only thing you can update on a resource attr)

        Args:
            resource_attr_id (int): ID of the complex model to be updated
            is_var           (unicode): 'Y' or 'N'

        Returns:
            List(complexmodels.ResourceAttr): Updated ResourceAttr

        Raises:
            ResourceNotFoundError if the resource_attr_id is not in the DB
        """
        updated_ra = attributes.update_resource_attribute(resource_attr_id,
                                                          is_var,
                                                          **ctx.in_header.__dict__)
        return ResourceAttr(updated_ra)


    @rpc(Integer, _returns=Unicode)
    def delete_resourceattr(ctx, resource_attr_id):
        """
        Deletes a resource attribute and all associated data.
        ***WILL BE DEPRECATED***

        Args:
            resource_attr_id (int): ID of the complex model to be deleted

        Returns:
            unicode: 'OK'

        Raises:
            ResourceNotFoundError if the resource_attr_id is not in the DB

        """
        attributes.delete_resource_attribute(resource_attr_id, **ctx.in_header.__dict__)

        return 'OK'

    @rpc(Integer, _returns=Unicode)
    def delete_resource_attribute(ctx,resource_attr_id):
        """
        Add a resource attribute attribute to a resource (Duplicate of delete_resourceattr)

        Args:
            resource_attr_id (int): ID of the complex model to be deleted

        Returns:
            unicode: 'OK'

        Raises:
            ResourceNotFoundError if the resource_attr_id is not in the DB

        """
        attributes.delete_resource_attribute(resource_attr_id,                                                                       **ctx.in_header.__dict__)

        return "OK"


    @rpc(Integer, Integer, Unicode(pattern="['YN']", default='N'), _returns=ResourceAttr)
    def add_network_attribute(ctx,network_id, attr_id, is_var):
        """
        Add a resource attribute to a network.

        Args:
            network_id (int): ID of the network
            attr_id    (int): ID of the attribute to assign to the network
            is_var     (string) 'Y' or 'N'. Indicates whether this attribute is
                a variable or not. (a variable is typically the result of a model run,
                so therefore doesn't need data assigned to it initially)

        Returns:
            complexmodels.ResourceAttr: A complex model of the newly created resource attribute.
        Raises:
            ResourceNotFoundError: If the network or attribute are not in the DB.
            HydraError           : If the attribute is already on the network.

        """
        new_ra = attributes.add_resource_attribute(
                                                       'NETWORK',
                                                       network_id,
                                                       attr_id,
                                                       is_var,
                                                       **ctx.in_header.__dict__)

        return ResourceAttr(new_ra)


    @rpc(Integer, Integer, _returns=SpyneArray(ResourceAttr))
    def add_network_attrs_from_type(ctx, type_id, network_id):
        """
        Adds all the attributes defined by a type to a network.

        Args:
            type_id    (int): ID of the type used to get the resource attributes from
            network_id (int): ID of the network

        Returns:
            List(complexmodels.ResourceAttr): All the newly created network attributes

        Raises:
            ResourceNotFoundError if the type_id or network_id are not in the DB
        """
        new_resource_attrs = attributes.add_resource_attrs_from_type(
                                                        type_id,
                                                        'NETWORK',
                                                        network_id,
                                                        **ctx.in_header.__dict__)

        return [ResourceAttr(ra) for ra in new_resource_attrs]


    @rpc(Integer, Unicode, Integer, _returns=SpyneArray(ResourceAttr))
    def add_resource_attrs_from_type(ctx, type_id, resource_type, resource_id):
        """
        Adds all the attributes defined by a type to a group.

        Args:
            type_id (int): ID of the type used to get the resource attributes from
            resource_type (string): NODE | LINK | GROUP | NETWORK
            resource_id (int): ID of the resource

        Returns:
            List(complexmodels.ResourceAttr): All the newly created resource attributes

        Raises:
            ResourceNotFoundError if the type_id or group_id are not in the DB

        """

        new_resource_attrs = attributes.add_resource_attrs_from_type(
                                                        type_id,
                                                        resource_type,
                                                        resource_id,
                                                        **ctx.in_header.__dict__)
        return [ResourceAttr(ra) for ra in new_resource_attrs]

    @rpc(Unicode, Integer, Integer(min_occurs=0, max_occurs=1), _returns=SpyneArray(AnyDict))
    def get_resource_attributes(ctx, ref_key, ref_id, type_id):
        """
        Get all a resources's attributes

        Args:
            ref_id (int): ID of the network / node / link / group
            ref_key (string): NODE, LINK, GROUP, NETWORK
            type_id (int) (optional): ID of the type. If specified will only return the resource attributes relative to that type

        Returns:
            List(complexmodels.ResourceAttr): All the resource's attributes

        Raises:
            ResourceNotFoundError if the type_id or resource id are not in the DB


        """
        if ref_key is None or ref_id is None:
            raise HydraError(f"Resource Type {ref_key} or Resource ID {ref_id} is None")

        resource_attrs = attributes.get_resource_attributes(
            ref_key,
            ref_id,
            type_id)

        ret_data = [JSONObject(ra) for ra in resource_attrs]

        return ret_data

    @rpc(Unicode, Integer, Integer(min_occurs=0, max_occurs=1), _returns=SpyneArray(ResourceAttr))
    def get_all_resource_attributes(ctx, resource_type, resource_id, template_id):
        """
        Get all the resource attributes for all the nodes in the network.

        Args:
            resource_type (string): NODE | LINK | GROUP | NETWORK
            resource_id (int): The ID of the network that you want the node attributes from
            template_id (int) (optional): If this is specified, then it will only return the attributes in this template.

        Returns:
            List(complexmodels.ResourceAttr): The resource attributes of all the nodes in the resource.
        """
        resource_attrs = attributes.get_all_resource_attributes(
                resource_type,
                resource_id,
                template_id)

        return [ResourceAttr(ra) for ra in resource_attrs]


    @rpc(Integer, Integer(default=None), _returns=SpyneArray(ResourceAttr))
    def get_all_network_attributes(ctx, network_id, template_id):
        """
            Get all the attributes for all the nodes, links and groups in the network
            including network attributes. This is used primarily to avoid retrieving
            all global attributes for menus etc, most of which are not necessary.

            args:
                network_id (int): The ID of the network containing the attributes
                template_id (int): A filter which will cause the function to
                                    return attributes associated to that template

            returns:
                A list of Attributes as JSONObjects, with the
                additional data of 'attr_is_var'
                from its assocated ResourceAttribute. ex:
                    {id:123,
                    name: 'cost'
                    dimension_id: 124,
                    attr_is_var: 'Y' #comes from the ResourceAttr
                    }
        """
        network_attributes = attributes.get_all_network_attributes(network_id,
                                                                   template_id,
                                                                   **ctx.in_header.__dict__)
        return [ResourceAttr(ra) for ra in network_attributes]

    @rpc(Integer, Integer(min_occurs=0, max_occurs=1), _returns=SpyneArray(ResourceAttr))
    def get_network_attributes(ctx, network_id, type_id):
        """
        Get all a network's attributes (not the attributes of the nodes and links. just the network itself).

        Args:
            network_id (int): ID of the network
            type_id    (int) (optional): ID of the type. If specified will only return the resource attributes relative to that type

        Returns:
            List(complexmodels.ResourceAttr): All the network attributes

        Raises:
            ResourceNotFoundError if the type_id or network_id are not in the DB


        """
        print("Getting attributes")
        resource_attrs = attributes.get_resource_attributes(
                'NETWORK',
                network_id,
                type_id)
        print("Got attributes")
        return_vals = [ResourceAttr(ra) for ra in resource_attrs]
        print("Returning data")
        return return_vals


    @rpc(Integer, Integer, Unicode(pattern="['YN']", default='N'), _returns=ResourceAttr)
    def add_node_attribute(ctx,node_id, attr_id, is_var):
        """
        Add a resource attribute to a node.

        Args:
            node_id (int): The ID of the Node
            attr_id (int): The ID if the attribute being added.
            is_var (char): Y or N. Indicates whether the attribute is a variable or not.

        Returns:
            complexmodels.ResourceAttr: The newly created node attribute

        Raises:
            ResourceNotFoundError: If the node or attribute do not exist
            HydraError: If this addition causes a duplicate attribute on the node.

        """
        new_ra = attributes.add_resource_attribute(
                                                       'NODE',
                                                       node_id,
                                                       attr_id,
                                                       is_var,
                                                       **ctx.in_header.__dict__)

        return ResourceAttr(new_ra)


    @rpc(Integer, Integer, _returns=SpyneArray(ResourceAttr))
    def add_node_attrs_from_type(ctx, type_id, node_id):
        """
        Adds all the attributes defined by a type to a node.

        Args:
            type_id (int): ID of the type used to get the resource attributes from
            node_id (int): ID of the node

        Returns:
            List(complexmodels.ResourceAttr): All the newly created node attributes

        Raises:
            ResourceNotFoundError if the type_id or node_id are not in the DB

        """
        new_resource_attrs = attributes.add_resource_attrs_from_type(
                                                        type_id,
                                                        'NODE',
                                                        node_id,
                                                        **ctx.in_header.__dict__)
        return [ResourceAttr(ra) for ra in new_resource_attrs]

    @rpc(Integer, Integer(min_occurs=0, max_occurs=1), _returns=SpyneArray(ResourceAttr))
    def get_node_attributes(ctx, node_id, type_id):
        """
        Get all a node's attributes.

        Args:
            node_id (int): ID of the node
            type_id (int) (optional): ID of the type. If specified will only return the resource attributes relative to that type

        Returns:
            List(complexmodels.ResourceAttr): All the node's attributes

        Raises:
            ResourceNotFoundError if the type_id or node_id do not exist.
        """

        resource_attrs = attributes.get_resource_attributes(
                'NODE',
                node_id,
                type_id)

        return [ResourceAttr(ra) for ra in resource_attrs]

    @rpc(Integer, Integer(min_occurs=0, max_occurs=1), _returns=SpyneArray(ResourceAttr))
    def get_all_node_attributes(ctx, network_id, template_id):
        """
        Get all the resource attributes for all the nodes in the network.

        Args:
            network_id (int): The ID of the network that you want the node attributes from
            template_id (int) (optional): If this is specified, then it will only return the attributes in this template.

        Returns:
            List(complexmodels.ResourceAttr): The resource attributes of all the nodes in the network.
        """
        resource_attrs = attributes.get_all_resource_attributes(
                'NODE',
                network_id,
                template_id)

        return [ResourceAttr(ra) for ra in resource_attrs]

    @rpc(Integer, Integer, Unicode(pattern="['YN']", default='N'), _returns=ResourceAttr)
    def add_link_attribute(ctx,link_id, attr_id, is_var):
        """
        Add a resource attribute to a link.

        Args:
            link_id (int): The ID of the Link
            attr_id (int): The ID if the attribute being added.
            is_var (char): Y or N. Indicates whether the attribute is a variable or not.

        Returns:
            complexmodels.ResourceAttr: The newly created link attribute

        Raises:
            ResourceNotFoundError: If the link or attribute do not exist
            HydraError: If this addition causes a duplicate attribute on the link.

        """
        new_ra = attributes.add_resource_attribute(
                                                       'LINK',
                                                       link_id,
                                                       attr_id,
                                                       is_var,
                                                       **ctx.in_header.__dict__)

        return ResourceAttr(new_ra)


    @rpc(Integer, Integer, _returns=SpyneArray(ResourceAttr))
    def add_link_attrs_from_type(ctx, type_id, link_id):
        """
        Adds all the attributes defined by a type to a link.

        Args:
            type_id (int): ID of the type used to get the resource attributes from
            link_id (int): ID of the link

        Returns:
            List(complexmodels.ResourceAttr): All the newly created link attributes

        Raises:
            ResourceNotFoundError if the type_id or link_id are not in the DB

        """

        new_resource_attrs = attributes.add_resource_attrs_from_type(
                                                        type_id,
                                                        'LINK',
                                                        link_id,
                                                        **ctx.in_header.__dict__)
        return [ResourceAttr(ra) for ra in new_resource_attrs]

    @rpc(Integer, Integer(min_occurs=0, max_occurs=1), _returns=SpyneArray(ResourceAttr))
    def get_link_attributes(ctx, link_id, type_id):
        """
        Get all a link's attributes.

        Args:
            link_id (int): ID of the link
            type_id (int) (optional): ID of the type. If specified will only return the resource attributes relative to that type

        Returns:
            List(complexmodels.ResourceAttr): All the link's attributes

        Raises:
            ResourceNotFoundError if the type_id or link_id do not exist.
        """

        resource_attrs = attributes.get_resource_attributes(
                'LINK',
                link_id,
                type_id)

        return [ResourceAttr(ra) for ra in resource_attrs]

    @rpc(Integer, Integer(min_occurs=0, max_occurs=1), _returns=SpyneArray(ResourceAttr))
    def get_all_link_attributes(ctx, network_id, template_id):
        """
        Get all the resource attributes for all the links in the network.

        Args:
            network_id (int): The ID of the network that you want the link attributes from
            template_id (int) (optional): If this is specified, then it will only return the attributes in this template.

        Returns:
            List(complexmodels.ResourceAttr): The resource attributes of all the links in the network.
        """

        resource_attrs = attributes.get_all_resource_attributes(
                'LINK',
                network_id,
                template_id)

        return [ResourceAttr(ra) for ra in resource_attrs]

    @rpc(Integer, Integer, Unicode(pattern="['YN']", default='N'), _returns=ResourceAttr)
    def add_group_attribute(ctx,group_id, attr_id, is_var):
        """
        Add a resource attribute to a group.

        Args:
            group_id (int): The ID of the Group
            attr_id (int): THe ID if the attribute being added.
            is_var (char): Y or N. Indicates whether the attribute is a variable or not.

        Returns:
            complexmodels.ResourceAttr: The newly created group attribute

        Raises:
            ResourceNotFoundError: If the group or attribute do not exist
            HydraError: If this addition causes a duplicate attribute on the group.

        """

        new_ra = attributes.add_resource_attribute(
                                                       'GROUP',
                                                       group_id,
                                                       attr_id,
                                                       is_var,
                                                       **ctx.in_header.__dict__)

        return ResourceAttr(new_ra)


    @rpc(Integer, Integer, _returns=SpyneArray(ResourceAttr))
    def add_group_attrs_from_type(ctx, type_id, group_id):
        """
        Adds all the attributes defined by a type to a group.

        Args:
            type_id (int): ID of the type used to get the resource attributes from
            group_id (int): ID of the group

        Returns:
            List(complexmodels.ResourceAttr): All the newly created group attributes

        Raises:
            ResourceNotFoundError if the type_id or group_id are not in the DB

        """
        new_resource_attrs = attributes.add_resource_attrs_from_type(
                                                        type_id,
                                                        'GROUP',
                                                        group_id,
                                                        **ctx.in_header.__dict__)
        return [ResourceAttr(ra) for ra in new_resource_attrs]

    @rpc(Integer, Integer(min_occurs=0, max_occurs=1), _returns=SpyneArray(ResourceAttr))
    def get_group_attributes(ctx, group_id, type_id):
        """
        Get all a group's attributes.

        Args:
            group_id (int): ID of the group
            type_id (int) (optional): ID of the type. If specified will only return the resource attributes relative to that type

        Returns:
            List(complexmodels.ResourceAttr): All the group's attributes

        Raises:
            ResourceNotFoundError if the type_id or group_id do not exist.
        """

        resource_attrs = attributes.get_resource_attributes(
                'GROUP',
                group_id,
                type_id,
                **ctx.in_header.__dict__)

        return [ResourceAttr(ra) for ra in resource_attrs]

    @rpc(Integer, Integer(min_occurs=0, max_occurs=1), _returns=SpyneArray(ResourceAttr))
    def get_all_group_attributes(ctx, network_id, template_id):
        """
        Get all the resource attributes for all the groups in the network.

        Args:
            network_id (int): The ID of the network that you want the group attributes from
            template_id (int) (optional): If this is specified, then it will only return the attributes in this template.

        Returns:
            List(complexmodels.ResourceAttr): The resource attributes of all the groups in the network.
        """


        resource_attrs = attributes.get_all_resource_attributes(
                'GROUP',
                network_id,
                template_id,
                **ctx.in_header.__dict__)

        return [ResourceAttr(ra) for ra in resource_attrs]


    @rpc(Integer, _returns=Unicode)
    def check_attr_dimension(ctx, attr_id):
        """
        Check that the dimension of the resource attribute data is consistent
        with the definition of the attribute.
        If the attribute says 'volume', make sure every dataset connected
        with this attribute via a resource attribute also has a dimension
        of 'volume'.

        Args:
            attr_id (int): The ID of the attribute you want to check

        Returns:
            string: 'OK' if all is well.

        Raises:
            HydraError: If a dimension mismatch is found.
        """

        attributes.check_attr_dimension(attr_id, **ctx.in_header.__dict__)

        return 'OK'

    @rpc(Integer, Integer, _returns=Unicode)
    def set_attribute_mapping(ctx, resource_attr_a, resource_attr_b):
        """
        Define one resource attribute from one network as being the same as
        that from another network.

        Args:
            resource_attr_a (int): The ID of the source resoure attribute
            resource_attr_b (int): The ID of the target resoure attribute

        Returns:
            string: 'OK' if all is well.

        Raises:
            ResourceNotFoundError: If either resource attribute is not found.
        """
        attributes.set_attribute_mapping(resource_attr_a, resource_attr_b, **ctx.in_header.__dict__)

        return 'OK'

    @rpc(Integer, Integer, _returns=Unicode)
    def delete_attribute_mapping(ctx, resource_attr_a, resource_attr_b):
        """
        Delete a mapping which said one resource attribute from one network
        was the same as the resource attribute in another.

        Args:
            resource_attr_a (int): The ID of the source resoure attribute
            resource_attr_b (int): The ID of the target resoure attribute

        Returns:
            string: 'OK' if all is well. If the mapping isn't there, it'll still return 'OK', so make sure the IDs are correct!

        """
        attributes.delete_attribute_mapping(resource_attr_a, resource_attr_b, **ctx.in_header.__dict__)

        return 'OK'

    @rpc(Integer, Integer(min_occurs=0, max_occurs=1), _returns=SpyneArray(ResourceAttrMap))
    def get_mappings_in_network(ctx, network_id, network_2_id):
        """
        Get all the resource attribute mappings in a network (both from and to). If another network
        is specified, only return the mappings between the two networks.

        Args:
            network_id (int): The network you want to check the mappings of (both from and to)
            network_2_id (int) (optional): The partner network

        Returns:
            List(complexmodels.ResourceAttrMap): All the mappings to and from the network(s) in question.
        """
        mapping_rs = attributes.get_mappings_in_network(network_id, network_2_id, **ctx.in_header.__dict__)

        mappings = [ResourceAttrMap(m) for m in mapping_rs]
        return mappings

    @rpc(Integer, Integer(min_occurs=0, max_occurs=1), _returns=Unicode)
    def delete_mappings_in_network(ctx, network_id, network_2_id):
        """
        Delete all the resource attribute mappings in a network. If another network
        is specified, only delete the mappings between the two networks.

        Args:
            network_id (int): The network you want to delete the mappings from (both from and to)
            network_2_id (int) (optional): The partner network

        Returns:
            string: 'OK'
        """
        attributes.delete_mappings_in_network(network_id, network_2_id, **ctx.in_header.__dict__)

        return 'OK'

    @rpc(Integer, Integer(min_occurs=0, max_occurs=1), _returns=SpyneArray(ResourceAttrMap))
    def get_node_mappings(ctx, node_id, node_2_id):
        """
        Get the mappings for all the attributes of a given node. If a second node
        is specified, return only the mappings between these nodes..

        Args:
            node_id (int): The node you want to delete the mappings from (both from and to)
            node_2_id (int) (optional): The partner node

        Returns:
            List(complexmodels.ResourceAttrMap): All the mappings to and from the node(s) in question.
        """
        mapping_rs = attributes.get_node_mappings(node_id, node_2_id, **ctx.in_header.__dict__)

        mappings = [ResourceAttrMap(m) for m in mapping_rs]
        return mappings


    @rpc(Integer, Integer, _returns=Unicode)
    def check_attribute_mapping_exists(ctx, resource_attr_id_source, resource_attr_id_target):
        """
        Check whether a mapping exists between two resource attributes
        This does not check whether a reverse mapping exists, so order is important here.

        Args:
            resource_attr_id_source (int): The source resource attribute
            resource_attr_id_target (int) (optional): The target resource attribute

        Returns:
            string: 'Y' if a mapping between the source and target exists. 'N' in every other case.

        """
        is_mapped = attributes.check_attribute_mapping_exists(resource_attr_id_source, resource_attr_id_target,**ctx.in_header.__dict__)

        return is_mapped

class AttributeGroupService(HydraService):
    @rpc(Integer, _returns=AttrGroup)
    def get_attribute_group(ctx, group_id):
        """

        """
        group_i = attributes.get_attribute_group(group_id, **ctx.in_header.__dict__)

        return AttrGroup(group_i)

    @rpc(AttrGroup, _returns=AttrGroup)
    def add_attribute_group(ctx, attributegroup):
        """
            Add a new attribute group.

            An attribute group is a container for attributes which need to be grouped
            in some logical way. For example, if the 'attr_is_var' flag isn't expressive
            enough to delineate different groupings.

            an attribute group looks like:
                {
                    'project_id' : XXX,
                    'name'       : 'my group name'
                    'description : 'my group description' (optional)
                    'layout'     : 'my group layout'      (optional)
                    'exclusive'  : 'N' (or 'Y' )          (optional, default to 'N')
                }
        """

        newgroup_i = attributes.add_attribute_group(attributegroup, **ctx.in_header.__dict__)

        return AttrGroup(newgroup_i)

    @rpc(AttrGroup, _returns=AttrGroup)
    def update_attribute_group(ctx, attributegroup):
        """
            Update an existing attribute group.

            An attribute group is a container for attributes which need to be grouped
            in some logical way. For example, if the 'attr_is_var' flag isn't expressive
            enough to delineate different groupings.

            an attribute group looks like:
                {
                    'project_id' : XXX,
                    'name'       : 'my group name'
                    'description : 'my group description' (optional)
                    'layout'     : 'my group layout'      (optional)
                    'exclusive'  : 'N' (or 'Y' )          (optional, default to 'N')
                }
        """

        updated_group_i = attributes.update_attribute_group(attributegroup, **ctx.in_header.__dict__)
        return AttrGroup(updated_group_i)

    @rpc(Integer, _returns=Unicode)
    def delete_attribute_group(ctx, group_id):
        """
            Delete an attribute group.
        """

        status = attributes.delete_attribute_group(group_id, **ctx.in_header.__dict__)

        return status

    @rpc(Integer, _returns=SpyneArray(AttrGroupItem))
    def get_network_attributegroup_items(ctx, network_id):
        """
            Get all the group items in a network
        """

        agis = attributes.get_network_attributegroup_items(network_id, **ctx.in_header.__dict__)

        complex_agis = [AttrGroupItem(agi) for agi in agis]

        return complex_agis

    @rpc(Integer, Integer, _returns=SpyneArray(AttrGroupItem))
    def get_group_attributegroup_items(ctx, network_id, group_id):
        """
            Get all the items in a specified group, within a network
        """

        agis = attributes.get_group_attributegroup_items(network_id, group_id, **ctx.in_header.__dict__)

        complex_agis = [AttrGroupItem(agi) for agi in agis]

        return complex_agis

    @rpc(Integer, Integer, _returns=SpyneArray(AttrGroupItem))
    def get_attribute_item_groups(ctx, network_id, attr_id):
        """
            Get all the group items in a network with a given attribute_id
        """

        agis = attributes.get_attribute_item_groups(network_id, attr_id, **ctx.in_header.__dict__)

        complex_agis = [AttrGroupItem(agi) for agi in agis]

        return complex_agis

    @rpc(SpyneArray(AttrGroupItem), _returns=SpyneArray(AttrGroupItem))
    def add_attribute_group_items(ctx, attributegroupitems):
        """
            Populate attribute groups with items.
            ** attributegroupitems : a list of items, of the form:
                ```{
                        'attr_id'    : X,
                        'group_id'   : Y,
                        'network_id' : Z,
                   }```

            Note that this approach supports the possibility of populating groups
            within multiple networks at the same time.

            When adding a group item, the function checks whether it can be added,
            based on the 'exclusivity' setup of the groups -- if a group is specified
            as being 'exclusive', then any attributes within that group cannot appear
            in any other group (within a network).
        """

        agis = attributes.add_attribute_group_items(attributegroupitems, **ctx.in_header.__dict__)

        complex_agis = [AttrGroupItem(agi) for agi in agis]

        return complex_agis

    @rpc(SpyneArray(AttrGroupItem), _returns=Unicode)
    def delete_attribute_group_items(ctx, attributegroupitems):
        """
            remove attribute groups items .
            ** attributegroupitems : a list of items, of the form:
                ```{
                        'attr_id'    : X,
                        'group_id'   : Y,
                        'network_id' : Z,
                   }```
        """

        status = attributes.delete_attribute_group_items(attributegroupitems, **ctx.in_header.__dict__)

        return status

    @rpc(_returns=Unicode)
    def delete_all_duplicate_attributes(ctx):
        """
            duplicate attributes can appear i the DB when attributes are added
            with a dimension of None (because muysql allows multiple entries
            even if there is a unique constraint where one of the values is null)

            This identifies one attribute of a duplicate set and then remaps all pointers to duplicates
            to that attribute, before deleting all other duplicate attributes.

            steps are:
                1: Identify all duplicate attributes
                2: Select one of the duplicates to be the one to keep
                3: Remap all resource attributes and type attributes to point from
                   duplicate attrs to the keeper.
                4: Delete the duplicates.
        """

        attributes.delete_all_duplicate_attributes(**ctx.in_header.__dict__)

    @rpc(_returns=Unicode)
    def delete_duplicate_resourceattributes(ctx):
        """
        for every resource, find any situations where there are duplicate attribute
        names, ex 2 max_flows, but where the attribute IDs are different. In this case,
        remove one of them, and keep the one which is used in the template for that node.
        """
        attributes.delete_duplicate_resourceattributes(**ctx.in_header.__dict__)
