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

from spyne.model.complex import Array as SpyneArray, ComplexModel
from spyne.model.primitive import Unicode
from spyne.model.primitive import Integer
from spyne.model.primitive import Decimal
from spyne.model.primitive import AnyDict
from spyne.model.primitive import Double
from decimal import Decimal as Dec
import pandas as pd
import logging
from hydra_base.util import generate_data_hash
import json
import zlib
from hydra_base import config
from hydra_base.util import get_json_as_dict, get_json_as_string

from hydra_base.lib.HydraTypes.Registry import HydraObjectFactory
from hydra_base.exceptions import HydraError
import six

from hydra_base.lib.objects import JSONObject, Dataset

NS = "server.complexmodels"
log = logging.getLogger(__name__)

class HydraComplexModel(ComplexModel):
    """
    This is the superclass from which most hydra complex models inherit.
    It contains the namespace 'server.complexmodels', which all
    hydra complex models need.
    """
    __namespace__ = 'server.complexmodels'

    def get_outgoing_layout(self, resource_layout):
        return get_json_as_dict(resource_layout)

class LoginResponse(HydraComplexModel):
    """
    """
    __namespace__ = 'server.complexmodels'
    _type_info = [
        ('user_id',  Integer(min_occurs=1)),
    ]

class ResourceData(HydraComplexModel):
    """
        An object which represents a resource attr, resource scenario and dataset
        all in one.


        * **attr_id:** The ID of the attribute to which this data belongs
        * **scenario_id:** The ID of the scenario in which this data has been assigned
        * **resource_attr_id:** The unique ID representing the attribute and resource combination
        * **ref_key:** Indentifies the type of resource to which this dataset is attached. Can be 'NODE', 'LINK', 'GROUP', 'NETWORK' or 'PROJECT'
        * **ref_id:** The ID of the node, link, group, network, or project in question
        * **attr_is_var:** Flag to indicate whether this resource's attribute is a variable and hence should be filled in by a model
        * **dataset_id:** The ID of the dataset which has been assigned to the resource attribute
        * **dataset_type:** The type of the dataset -- can be scalar, descriptor, array or timeseries
        * **dataset_dimension:** The dimension of the dataset (This MUST match the dimension of the attribute)
        * **dataset_unit:** The unit of the dataset.
        * **dataset_name:** The name of the dataset. Most likely used for distinguishing similar datasets or searching for datasets
        * **dataset_hidden:** Indicates whether the dataset is hidden, in which case only authorised users can use the dataset.
        * **dataset_metadata:**: A dictionary of the metadata associated with the dataset. For example: {'created_by': "User 1", "source":"Import from CSV"}
        * **dataset_value:**
            Depending on what the dataset_type is, this can be a decimal value, a freeform
            string or a JSON string.
            For a timeseries for example, the datasset_value looks like:
            ::

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

    """
    _type_info = [
        ('attr_id',            Unicode(default=None)),
        ('attr_name',          Unicode(default=None)),
        ('scenario_id',        Unicode(default=None)),
        ('resource_attr_id',   Unicode(default=None)),
        ('ref_id',             Unicode(default=None)),
        ('ref_key',            Unicode(default=None)),
        ('ref_name',           Unicode(default=None)),
        ('attr_is_var',        Unicode(default=None)),
        ('dataset_id',         Unicode(default=None)),
        ('dataset_type',       Unicode(default=None)),
        ('dataset_dimension',  Unicode(default=None)),
        ('dataset_unit',       Integer(default=None)),
        ('dataset_name',       Unicode(default=None)),
        ('dataset_value',      Unicode(default=None)),
        ('dataset_hidden',     Unicode(default=None)),
        ('dataset_metadata',   Unicode(default=None)),
    ]

    def __init__(self, resourcedata=None, include_value='N'):

        super(ResourceData, self).__init__()
        if  resourcedata is None:
            return
        ra = resourcedata
        self.attr_id = str(ra.attr_id)
        self.attr_name = ra.attr_name
        self.attr_is_var = ra.attr_is_var
        self.resource_attr_id = str(ra.resource_attr_id)
        self.ref_key = str(ra.ref_key).upper()
        if ra.ref_key == 'NODE':
            self.ref_id  = ra.node_id
        elif ra.ref_key == 'LINK':
            self.ref_id = ra.link_id
        elif ra.ref_key == 'GROUP':
            self.ref_id = ra.link_id
        elif ra.ref_key == 'NETWORK':
            self.ref_id = ra.network_id
        self.ref_name  = ra.ref_name

        self.source = ra.source
        self.scenario_id = str(ra.scenario_id)

        self.dataset_hidden    = ra.hidden
        self.dataset_id        = str(ra.dataset_id)
        self.dataset_type      = ra.type
        self.dataset_name      = ra.dataset_name

        self.dataset_unit      = ra.unit_id
        if include_value=='Y':
            self.dataset_value = ra.value

        if ra.metadata:
            self.metadata = {}
            for m in ra.metadata:
                self.metadata[m.key] = m.value

            self.dataset_metadata = json.dumps(self.metadata)

class Dataset(HydraComplexModel):
    """
    - **id**               Integer(min_occurs=0, default=None)
    - **type**             Unicode
    - **dimension**        Unicode(min_occurs=1, default='dimensionless')
    - **unit**             Unicode(min_occurs=1, default=None)
    - **name**             Unicode(min_occurs=1, default=None)
    - **value**            Unicode(min_occurs=1, default=None)
    - **hidden**           Unicode(min_occurs=0, default='N' pattern="[YN]")
    - **created_by**       Integer(min_occurs=0, default=None)
    - **cr_date**          Unicode(min_occurs=0, default=None)
    - **hash**             Unicode(min_occurs=0, defaule=None)
    - **metadata**         Unicode(min_occurs=0, default='{}')
    """
    _type_info = [
        ('id', Integer(min_occurs=0, default=None)),
        ('type', Unicode),
        ('unit_id', Integer(min_occurs=1, default=None)),
        ('name', Unicode(min_occurs=1, default=None)),
        ('value',Unicode(min_occurs=1, default=None)),
        ('hidden', Unicode(min_occurs=0, default='N', pattern="[YN]")),
        ('created_by', Integer(min_occurs=0, default=None)),
        ('cr_date', Unicode(min_occurs=0, default=None)),
        ('hash', Unicode(min_occurs=0, default=None)),
        ('metadata', Unicode(min_occurs=0, default='{}')),
    ]

    def __init__(self, parent=None, include_metadata=True):
        super(Dataset, self).__init__()
        if  parent is None:
            return

        self.hidden = parent.hidden
        self.id = parent.id
        self.type = parent.type
        self.name = parent.name
        self.created_by = parent.created_by
        self.cr_date = str(parent.cr_date)
        self.hash = parent.hash

        self.unit_id = parent.unit_id
        self.value = None

        if parent.value is not None:
            try:
                self.value = zlib.decompress(parent.value)
            except:
                self.value = str(parent.value)

            if isinstance(self.value, dict) or isinstance(self.value, list):
                self.value = json.dumps(self.value)
            else:
                self.value = str(self.value)

        self.metadata = None

        if include_metadata is True:
            if isinstance(parent.metadata, dict):
                self.metadata = json.dumps(parent.metadata)
            elif hasattr(parent, 'metadata') and parent.metadata is not None:
                metadata = {}
                if parent.metadata:
                    for m in parent.metadata:
                        metadata[m.key] = str(m.value)
                self.metadata = json.dumps(metadata)

    def parse_value(self):
        """
            Turn the value of an incoming dataset into a hydra-friendly value.
        """
        try:
            if self.value is None:
                log.warning("Cannot parse dataset. No value specified.")
                return None

            # attr_data.value is a dictionary but the keys have namespaces which must be stripped
            data = six.text_type(self.value)

            if data.upper().strip() in ("NULL", ""):
                return "NULL"

            data = data[0:100]
            log.debug("[Dataset.parse_value] Parsing %s (%s)", data, type(data))

            return HydraObjectFactory.valueFromDataset(self.type, self.value, self.get_metadata_as_dict())

        except Exception as e:
            log.exception(e)
            raise HydraError("Error parsing value %s: %s"%(self.value, e))

    def get_metadata_as_dict(self, user_id=None, source=None):
        """
        Convert a metadata json string into a dictionary.

        Args:
            user_id (int): Optional: Insert user_id into the metadata if specified
            source (string): Optional: Insert source (the name of the app typically) into the metadata if necessary.

        Returns:
            dict: THe metadata as a python dictionary

        TODO this is a duplicate of the hydra_base dataset object function.
        """

        if self.metadata is None or self.metadata == "":
            return {}

        metadata_dict = self.metadata if isinstance(self.metadata, dict) else json.loads(self.metadata)

        # These should be set on all datasets by default, but we don't enforce this rigidly
        metadata_keys = [m.lower() for m in metadata_dict]
        if user_id is not None and 'user_id' not in metadata_keys:
            metadata_dict['user_id'] = six.text_type(user_id)

        if source is not None and 'source' not in metadata_keys:
            metadata_dict['source'] = six.text_type(source)

        return { k : six.text_type(v) for k, v in metadata_dict.items() }


    def get_hash(self, val, metadata):
        """
        TODO this is a duplicate of the hydra_base dataset object function.
        """

        if metadata is None:
            metadata = self.get_metadata_as_dict()

        if val is None:
            value = self.parse_value()
        else:
            value = val

        dataset_dict = {'name'     : self.name,
                        'unit_id'     : self.unit_id,
                        'type'     : self.type.lower(),
                        'value'    : value,
                        'metadata' : metadata,}

        data_hash = generate_data_hash(dataset_dict)

        return data_hash


class DatasetCollectionItem(HydraComplexModel):
    """
    - **collection_id** Integer
    - **dataset_id** Integer
    - **cr_date** Unicode(default=None)
    """
    _type_info = [
        ('collection_id', Integer),
        ('dataset_id', Integer),
        ('cr_date', Unicode(default=None)),
    ]

    def __init__(self, parent=None):
        super(DatasetCollectionItem, self).__init__()
        if  parent is None:
            return

        self.collection_id = parent.collection_id
        self.dataset_id = parent.dataset_id
        self.cr_date = str(parent.cr_date)


class DatasetCollection(HydraComplexModel):
    """
    - **name** Unicode(default=None)
    - **id** Integer(default=None)
    - **items** SpyneArray(Dataset) # Spyne array of dataset IDs
    - **cr_date** Unicode(default=None)
    """
    _type_info = [
        ('name', Unicode(default=None)),
        ('id', Integer(default=None)),
        ('items', SpyneArray(DatasetCollectionItem)),
        ('cr_date', Unicode(default=None)),
    ]

    def __init__(self, parent=None):
        super(DatasetCollection, self).__init__()
        if  parent is None:
            return
        self.name = parent.name
        self.id = parent.id
        self.items = [DatasetCollectionItem(d) for d in parent.items]
        self.cr_date = str(parent.cr_date)

class Attr(HydraComplexModel):
    """
       - **id** Integer(default=None)
       - **name** Unicode(default=None)
       - **dimension_id** Integer(default=None)
       - **description** Unicode(default=None)
       - **cr_date** Unicode(default=None)
    """
    _type_info = [
        ('id', Integer(default=None)),
        ('network_id', Integer(default=None)),
        ('project_id', Integer(default=None)),
        ('name', Unicode(default=None)),
        ('dimension_id', Integer(default=None)),
        ('dimension', Unicode(default=None)),#The dimension name, which is accepted on incoming requests in lieu of an ID
        ('description', Unicode(default=None)),
        ('cr_date', Unicode(default=None)),
    ]

    def __init__(self, parent=None):
        super(Attr, self).__init__()
        if  parent is None:
            return
        self.id = parent.id
        self.network_id = parent.network_id
        self.project_id = parent.project_id
        self.name = parent.name
        self.dimension = parent.dimension.name if parent.dimension and hasattr(parent.dimension, 'name') else parent.dimension
        self.dimension_id = parent.dimension_id

        self.description = parent.description
        self.cr_date = str(parent.cr_date)


class AttrGroup(HydraComplexModel):
    """
       - **id** Integer(default=None)
       - **project_id** Integer(default=None)
       - **name** Unicode(default=None)
       - **layout** AnyDict(min_occurs=0, max_occurs=1, default=None))
       - **description** Unicode(default=None)
       - **exclusive** Unicode(min_occurs=0, default='N')
       - **cr_date** Unicode(default=None)
    """
    _type_info = [
        ('id', Integer(default=None)),
        ('project_id', Integer(default=None)),
        ('name', Unicode(default=None)),
        ('layout', AnyDict(min_occurs=0, max_occurs=1, default=None)),
        ('description', Unicode(default=None)),
        ('exclusive', Unicode(min_occurs=0, default='N')),
        ('cr_date', Unicode(default=None)),
    ]

    def __init__(self, parent=None):
        super(AttrGroup, self).__init__()
        if  parent is None:
            return
        self.id = parent.id
        self.project_id  = parent.project_id
        self.name = parent.name
        self.description = parent.description
        self.exclusive = parent.exclusive
        self.cr_date = str(parent.cr_date)

class AttrGroupItem(HydraComplexModel):
    """
       - **group_id** Integer(default=None)
       - **attr_id** Integer(default=None)
       - **network_id** Integer(default=None)
    """
    _type_info = [
        ('group_id', Integer(default=None)),
        ('attr_id', Integer(default=None)),
        ('network_id', Integer(default=None)),
    ]

    def __init__(self, parent=None):
        super(AttrGroupItem, self).__init__()
        if  parent is None:
            return
        self.group_id = parent.group_id
        self.network_id = parent.network_id
        self.attr_id = parent.attr_id

class ResourceScenario(HydraComplexModel):
    """
       - **resource_attr_id** Integer(default=None)
       - **respourceattr**    ResourceAttr
       - **dataset_id**       Integer(default=None)
       - **dataset**          Dataset
       - **source**           Unicode
       - **cr_date**          Unicode(default=None)
       - **resourceattr**     ResourceAttr(default=None)
    """
    _type_info = [
        ('resource_attr_id', Integer(default=None)),
        ('resourceattr', AnyDict), #can't have resourceattr object as it's not been defined yet
        ('dataset_id', Integer(default=None)),
        ('scenario_id', Integer(default=None)),
        ('dataset', Dataset),
        ('source', Unicode),
        ('cr_date', Unicode(default=None)),
    ]

    def __init__(self, parent=None, attr_id=None):
        super(ResourceScenario, self).__init__()
        if parent is None:
            return
        self.resource_attr_id = parent.resource_attr_id
        self.resourceattr = {}
        if attr_id is not None:
            self.resourceattr['attr_id'] = attr_id
        elif hasattr(parent, 'resourceattr') and parent.resourceattr is not None:
            self.resourceattr['attr_id'] = parent.resourceattr.attr_id

        self.dataset_id = parent.dataset_id
        self.scenario_id = parent.scenario_id

        self.dataset = Dataset(parent.dataset)
        self.source = parent.source
        self.cr_date = str(parent.cr_date)

class ResourceAttr(HydraComplexModel):
    """
       - **id**      Integer(min_occurs=0, default=None)
       - **name**    Unicode(default="")
       - **attr_id** Integer(default=None)
       - **ref_id**  Integer(min_occurs=0, default=None)
       - **ref_key** Unicode(min_occurs=0, default=None)
       - **attr_is_var** Unicode(min_occurs=0, default='N')
       - **resourcescenario** ResourceScenario
       - **cr_date** Unicode(default=None)
    """
    _type_info = [
        ('id',      Integer(min_occurs=0, default=None)),
        ('name',    Unicode(default=None)),
        ('attr_id', Integer(default=None)),
        ('ref_id',  Integer(min_occurs=0, default=None)),
        ('ref_key', Unicode(min_occurs=0, default=None)),
        ('attr_is_var', Unicode(min_occurs=0, default='N')),
        ('resourcescenario', ResourceScenario),
        ('cr_date', Unicode(default=None)),
    ]

    def __init__(self, parent=None):
        super(ResourceAttr, self).__init__()
        if  parent is None:
            return
        self.id = parent.id
        if hasattr(parent, 'name'):
            self.name = parent.name

        if hasattr(parent, 'attr'):
            self.name = parent.attr.name

        self.attr_id = parent.attr_id
        self.ref_key  = parent.ref_key
        self.cr_date = str(parent.cr_date)
        if parent.ref_key == 'NETWORK':
            self.ref_id = parent.network_id
        elif parent.ref_key  == 'NODE':
            self.ref_id = parent.node_id
        elif parent.ref_key == 'LINK':
            self.ref_id = parent.link_id
        elif parent.ref_key == 'GROUP':
            self.ref_id = parent.group_id

        self.attr_is_var = parent.attr_is_var
        #This should be set externally as it is not related to its parent.
        self.resourcescenario = None

class ResourceAttrMap(HydraComplexModel):
    """
       - **resource_attr_id_a** Integer(default=None)
       - **resource_attr_id_b** Integer(default=None)
       - **attr_a_name**        Unicode(default=None)
       - **attr_b_name**        Unicode(default=None)
       - **ref_key_a**          Unicode(default=None)
       - **ref_key_b**          Unicode(default=None)
       - **ref_id_a**           Integer(default=None)
       - **ref_id_b**           Integer(default=None)
       - **resource_a_name**    Unicode(default=None)
       - **resource_b_name**    Unicode(default=None)
       - **network_a_id**       Integer(default=None)
       - **network_b_id**       Integer(default=None)
    """
    _type_info = [
        ('resource_attr_id_a', Integer(default=None)),
        ('resource_attr_id_b', Integer(default=None)),
        ('attr_a_name'       , Unicode(default=None)),
        ('attr_b_name'       , Unicode(default=None)),
        ('ref_key_a'         , Unicode(default=None)),
        ('ref_key_b'         , Unicode(default=None)),
        ('ref_id_a'          , Integer(default=None)),
        ('ref_id_b'          , Integer(default=None)),
        ('resource_a_name'   , Unicode(default=None)),
        ('resource_b_name'   , Unicode(default=None)),
        ('network_a_id'      , Integer(default=None)),
        ('network_b_id'      , Integer(default=None)),
    ]

    def __init__(self, parent=None):
        super(ResourceAttrMap, self).__init__()
        if  parent is None:
            return

        self.resource_attr_id_a = parent.resource_attr_id_a
        self.resource_attr_id_b = parent.resource_attr_id_b

        self.ref_key_a = parent.resourceattr_a.ref_key
        self.ref_id_a  = parent.resourceattr_a.get_resource_id()
        self.attr_a_name = parent.resourceattr_a.attr.name
        self.resource_a_name = parent.resourceattr_a.get_resource().get_name()

        self.ref_key_b = parent.resourceattr_b.ref_key
        self.ref_id_b  = parent.resourceattr_b.get_resource_id()
        self.attr_b_name = parent.resourceattr_b.attr.name
        self.resource_b_name = parent.resourceattr_b.get_resource().get_name()

        self.network_a_id = parent.network_a_id
        self.network_b_id = parent.network_b_id


class ResourceTypeDef(HydraComplexModel):
    """
       - **ref_key** Unicode(default=None)
       - **ref_id**  Integer(default=None)
       - **type_id** Integer(default=None)
    """
    _type_info = [
        ('ref_key', Unicode(default=None)),
        ('ref_id',  Integer(default=None)),
        ('type_id', Integer(default=None)),
        ('template_id', Integer(default=None)),
    ]

class TypeAttr(HydraComplexModel):
    """
       - **attr_id**            Integer(min_occurs=1, max_occurs=1)
       - **attr_name**          Unicode(default=None)
       - **type_id**            Integer(default=None)
       - **data_type**          Unicode(default=None)
       - **dimension**          Unicode(default=None)
       - **unit**               Unicode(default=None)
       - **default_dataset_id** Integer(default=None)
       - **data_restriction**   AnyDict(default=None)
       - **is_var**             Unicode(default=None)
       - **description**        Unicode(default=None)
       - **properties**         AnyDict(default=None)
       - **cr_date**            Unicode(default=None)
    """
    _type_info = [
        ('id', Integer(default=None)),
        ('parent_id', Integer(default=None)),
        ('attr_id', Integer(default=None)),
        ('attr', Attr),
        ('type_id', Integer(default=None)),
        ('data_type', Unicode(default=None)),
        ('dimension_id', Integer(default=None)),
        ('unit_id', Integer(default=None)),
        ('default_dataset', Dataset),
        ('data_restriction', AnyDict(default=None)),
        ('is_var', Unicode(default=None)),
        ('description', Unicode(default=None)),
        ('properties', AnyDict(default=None)),
        ('cr_date', Unicode(default=None)),
        ('status', Unicode(default='A', pattern="[AX]")),
    ]

    def __init__(self, parent=None):
        super(TypeAttr, self).__init__()
        if  parent is None:
            return

        self.id = parent.id
        self.parent_id = parent.parent_id
        self.attr_id = int(parent.attr_id)
        self.status = parent.status

        attr = parent.attr
        if attr:
            self.attr = Attr(attr)

        self.type_id = parent.type_id
        self.data_type = parent.data_type
        self.unit_id = parent.unit_id

        if parent.default_dataset is not None:
            self.default_dataset = Dataset(parent.default_dataset)
        self.status = parent.status
        self.description = parent.description
        self.properties = self.get_outgoing_layout(parent.properties)
        self.cr_date = str(parent.cr_date)
        self.data_restriction = self.get_outgoing_layout(parent.data_restriction)
        self.is_var = parent.attr_is_var

    def get_properties(self):
        if hasattr(self, 'properties') and self.properties is not None:
            return str(self.properties).replace('{%s}'%NS, '')
        else:
            return None

class TemplateType(HydraComplexModel):
    """
       - **id**          Integer(default=None)
       - **name**        Unicode(default=None)
       - **resource_type** Unicode(values=['GROUP', 'NODE', 'LINK', 'NETWORK'], default=None)
       - **alias**       Unicode(default=None)
       - **layout**      AnyDict(min_occurs=0, max_occurs=1, default=None)
       - **template_id** Integer(min_occurs=1, default=None)
       - **typeattrs**   SpyneArray(TypeAttr)
       - **cr_date**     Unicode(default=None)
    """
    _type_info = [
        ('id',          Integer(default=None)),
        ('parent_id', Integer(default=None)),
        ('name',        Unicode(default=None)),
        ('resource_type', Unicode(values=['GROUP', 'NODE', 'LINK', 'NETWORK'], default=None)),
        ('alias',       Unicode(default=None)),
        ('status',       Unicode(default=None)),
        ('layout',      AnyDict(min_occurs=0, max_occurs=1, default=None)),
        ('template_id', Integer(min_occurs=0, max_occurs=1, default=None)),
        ('typeattrs',   SpyneArray(TypeAttr)),
        ('cr_date',     Unicode(default=None)),
        ('status',      Unicode(default='A', pattern="[AX]")),
    ]

    def __init__(self, parent=None):
        super(TemplateType, self).__init__()
        if parent is None:
            return

        self.id        = parent.id
        self.template_id = parent.template_id
        self.parent_id = parent.parent_id
        self.name      = parent.name
        self.alias     = parent.alias
        self.status = parent.status
        self.resource_type = parent.resource_type
        self.cr_date = str(parent.cr_date)
        self.layout = self.get_outgoing_layout(parent.layout)
        self.template_id  = parent.template_id
        self.status = parent.status

        typeattrs = []
        for typeattr in parent.typeattrs:
            typeattrs.append(TypeAttr(typeattr))

        self.typeattrs = typeattrs

class Template(HydraComplexModel):
    """
       - **id**        Integer(default=None)
       - **name**      Unicode(default=None)
       - **layout**    AnyDict(min_occurs=0, max_occurs=1, default=None)
       - **types**     SpyneArray(TemplateType)
       - **cr_date**   Unicode(default=None)
    """
    _type_info = [
        ('id',        Integer(default=None)),
        ('parent_id', Integer(default=None)),
        ('status',       Unicode(default=None)),
        ('name',      Unicode(default=None)),
        ('layout',    AnyDict(min_occurs=0, max_occurs=1, default=None)),
        ('templatetypes', SpyneArray(TemplateType)),
        ('cr_date',   Unicode(default=None)),
    ]

    def __init__(self, parent=None):
        super(Template, self).__init__()
        if parent is None:
            return
        self.parent_id = parent.parent_id
        self.name   = parent.name
        self.status = parent.status
        self.parent_id = parent.parent_id
        self.id     = parent.id
        self.cr_date = str(parent.cr_date)
        self.layout = self.get_outgoing_layout(parent.layout)

        types = []
        for templatetype in parent.templatetypes:
            types.append(TemplateType(templatetype))
        self.templatetypes = types

class TypeSummary(HydraComplexModel):
    """
       - **type_name**    Unicode
       - **type_id**      Integer
       - **template_name** Unicode
       - **template_id** Integer
    """
    _type_info = [
        ('name',    Unicode),
        ('id',      Integer),
        ('type_name',    Unicode),
        ('type_id',      Integer),
        ('template_name', Unicode),
        ('template_id', Integer),
        ('child_template_id', Integer)
    ]

    def __init__(self, parent=None):
        super(TypeSummary, self).__init__()

        if parent is None:
            return

        self.child_template_id = parent.child_template_id

        if hasattr(parent, 'templatetype') and parent.templatetype is not None:
            # Here just if the parent contains templatetype and it is not None
            self.id = parent.templatetype.id
            self.name = parent.templatetype.name
            self.type_id = parent.templatetype.id
            self.type_name = parent.templatetype.name
            self.template_id = parent.templatetype.template_id
            if parent.templatetype.template is not None:
                self.template_name = parent.templatetype.template.name
        else:
            #if it's a resourcetype object
            if hasattr(parent, 'type_id') and parent.type_id is not None:
                self.id = parent.type_id
                self.type_id = parent.type_id
            else:
                self.id = parent.id
                self.type_id = parent.id

            if hasattr(parent, 'child_template_id'):
                self.child_template_id = parent.child_template_id

            self.name = parent.name
            self.template_name = getattr(parent, 'template_name', None)
            self.template_id = getattr(parent, "template_id", None)

class ValidationError(HydraComplexModel):
    """
       - **scenario_id**      Integer(default=None)
       - **ref_key**          Unicode(default=None)
       - **ref_id**           Integer(default=None)
       - **ref_name**         Unicode(default=None)
       - **attr_name**        Unicode(default=None)
       - **attr_id**          Integer(default=None)
       - **template_id**      Integer(default=None)
       - **type_id**          Integer(default=None)
       - **resource_attr_id** Integer(default=None)
       - **dataset_id**       Integer(default=None)
       - **error_text**       Unicode(default=None)
    """
    _type_info = [
        ('scenario_id',      Integer(default=None)),
        ('ref_key',          Unicode(default=None)),
        ('ref_id',           Integer(default=None)),
        ('ref_name',         Unicode(default=None)),
        ('attr_name',        Unicode(default=None)),
        ('attr_id',          Integer(default=None)),
        ('template_id',      Integer(default=None)),
        ('type_id',          Integer(default=None)),
        ('resource_attr_id', Integer(default=None)),
        ('dataset_id',       Integer(default=None)),
        ('error_text',       Unicode(default=None)),
    ]

    def __init__(self, error_text, scenario_id=None,
                 ref_key=None, ref_id=None, ref_name=None,
                 attr_name=None, attr_id=None,
                 template_id=None, type_id=None,
                 resource_attr_id=None, dataset_id=None):

        super(ValidationError, self).__init__()

        self.error_text       = error_text
        self.ref_key          = ref_key
        self.ref_id           = ref_id
        self.ref_name         = ref_name
        self.attr_name        = attr_name
        self.attr_id          = attr_id
        self.resource_attr_id = attr_id
        self.dataset_id       = dataset_id
        self.template_id      = template_id
        self.type_id          = type_id

class Resource(HydraComplexModel):
    """
        Superclass for anything which has a layout field:
            - nodes
            - links
            - network
            - scenario
            - project
    """

    def get_layout(self):
        if hasattr(self, 'layout') and self.layout is not None:
            return get_json_as_string(self.layout)
        else:
            return None

    def get_json(self, key):
        if not hasattr(self, key):
            return None

        attr = getattr(self, key)

        val = get_json_as_string(attr)

        if val:
            val = val.replace('{%s}'%NS, '')

        return val

class ResourceSummary(HydraComplexModel):
    """
       - **ref_key**     Unicode(default=None)
       - **id**          Integer(default=None)
       - **name**        Unicode(default=None)
       - **description** Unicode(min_occurs=1, default="")
       - **attributes**  SpyneArray(ResourceAttr)),
       - **types**       SpyneArray(TypeSummary)),
    """
    _type_info = [
        ('ref_key',     Unicode(default=None)),
        ('id',          Integer(default=None)),
        ('name',        Unicode(default=None)),
        ('appdata',     AnyDict(min_occurs=0, max_occurs=1, default=None)),
        ('description', Unicode(min_occurs=1, default="")),
        ('attributes',  SpyneArray(ResourceAttr)),
        ('types',       SpyneArray(TypeSummary)),
    ]

    def __init__(self, parent=None, include_attributes=True):
        """
            args:
                parent: The ORM or JSONObject representing the Node / Link / Group / Network / Project
                include_attributes: Include resource attributes or not. Setting to False is has significant performance benefits.
        """
        super(ResourceSummary, self).__init__()

        if parent is None:
            return

        self.id   = parent.id
        self.name = parent.name
        self.description = parent.description

        if hasattr(parent, 'node_id'):
            self.ref_key = 'NODE'
        elif hasattr(parent, 'link_id'):
            self.ref_key = 'LINK'
        elif hasattr(parent, 'group_id'):
            self.ref_key = 'GROUP'
        if hasattr(parent, 'appdata'):
            #this is a failsafe to ensure that the 'appdata' column
            #is processed correctly, as it is a JSON column type which may
            #not work with with serialising data.
            if parent.appdata is not None:
                if isinstance(parent.appdata, str):
                    parent_appdata = json.loads(parent.appdata)
                else:
                    parent_appdata = parent.appdata

                appdata = {}
                for k, v in parent_appdata.items():
                    appdata[k] = v

                self.appdata = appdata

        if include_attributes:
            self.attributes = [ResourceAttr(ra) for ra in parent.attributes]

        self.types = [TypeSummary(t) for t in parent.types]

class Node(Resource):
    """
       - **id**          Integer(default=None)
       - **name**        Unicode(default=None)
       - **description** Unicode(min_occurs=1, default="")
       - **layout**      AnyDict(min_occurs=0, max_occurs=1, default=None)
       - **x**           Double(min_occurs=1, default=0)
       - **y**           Double(min_occurs=1, default=0)
       - **status**      Unicode(default='A** pattern="[AX]")
       - **attributes**  SpyneArray(ResourceAttr)
       - **types**       SpyneArray(TypeSummary)
       - **cr_date**     Unicode(default=None)
    """
    _type_info = [
        ('id',          Integer(default=None)),
        ('name',        Unicode(default=None)),
        ('description', Unicode(min_occurs=0, default="")),
        ('layout',      AnyDict(min_occurs=0, max_occurs=1, default=None)),
        ('x',           Double(min_occurs=1, default=0)),
        ('y',           Double(min_occurs=1, default=0)),
        ('status',      Unicode(default='A', pattern="[AX]")),
        ('attributes',  SpyneArray(ResourceAttr)),
        ('types',       SpyneArray(TypeSummary)),
        ('cr_date',     Unicode(default=None)),
    ]

    def __init__(self, parent=None, include_attributes=True):
        super(Node, self).__init__()

        if parent is None:
            return


        self.id = parent.id
        self.name = parent.name
        self.x = float(parent.x)
        self.y = float(parent.y)
        self.description = parent.description
        self.cr_date = str(parent.cr_date)
        self.layout = self.get_outgoing_layout(parent.layout)
        self.status = parent.status
        if include_attributes is True:
            self.attributes = [ResourceAttr(a) for a in parent.attributes]
        self.types = [TypeSummary(t) for t in parent.types]



class Link(Resource):
    """
       - **id**          Integer(default=None)
       - **name**        Unicode(default=None)
       - **description** Unicode(min_occurs=1, default="")
       - **layout**      AnyDict(min_occurs=0, max_occurs=1, default=None)
       - **node_1_id**   Integer(default=None)
       - **node_2_id**   Integer(default=None))
       - **status**      Unicode(default='A** pattern="[AX]")
       - **attributes**  SpyneArray(ResourceAttr)
       - **types**       SpyneArray(TypeSummary)
       - **cr_date**     Unicode(default=None)
    """
    _type_info = [
        ('id',          Integer(default=None)),
        ('name',        Unicode(default=None)),
        ('description', Unicode(min_occurs=0, default="")),
        ('layout',      AnyDict(min_occurs=0, max_occurs=1, default=None)),
        ('node_1_id',   Integer(default=None)),
        ('node_2_id',   Integer(default=None)),
        ('status',      Unicode(default='A', pattern="[AX]")),
        ('attributes',  SpyneArray(ResourceAttr)),
        ('types',       SpyneArray(TypeSummary)),
        ('cr_date',     Unicode(default=None)),
    ]

    def __init__(self, parent=None, include_attributes=True):
        super(Link, self).__init__()

        if parent is None:
            return


        self.id = parent.id
        self.name = parent.name
        self.node_1_id = parent.node_1_id
        self.node_2_id = parent.node_2_id
        self.description = parent.description
        self.cr_date = str(parent.cr_date)
        self.layout = self.get_outgoing_layout(parent.layout)
        self.status    = parent.status
        if include_attributes is True:
            self.attributes = [ResourceAttr(a) for a in parent.attributes]
        self.types = [TypeSummary(t) for t in parent.types]


class AttributeData(HydraComplexModel):
    """
        A class which is returned by the server when a request is made
        for the data associated with an attribute.
       - **resourceattrs** SpyneArray(ResourceAttr)
       - **resourcescenarios** SpyneArray(ResourceScenario)
    """
    _type_info = [
        ('resourceattrs', SpyneArray(ResourceAttr)),
        ('resourcescenarios', SpyneArray(ResourceScenario)),
    ]

class ResourceGroupItem(HydraComplexModel):
    """
       - **id**       Integer(default=None)
       - **node_id**   Integer(default=None)
       - **link_id**   Integer(default=None)
       - **subgroup_id**   Integer(default=None)
       - **ref_key**  Unicode(default=None)
       - **group_id** Integer(default=None)
       - **cr_date**     Unicode(default=None)
    """
    _type_info = [
        ('id',       Integer(default=None)),
        ('node_id',   Integer(default=None)),
        ('link_id',   Integer(default=None)),
        ('subgroup_id', Integer(default=None)),
        ('ref_key',  Unicode(default=None)),
        ('group_id', Integer(default=None)),
        ('cr_date',     Unicode(default=None)),
    ]

    def __init__(self, parent=None):
        super(ResourceGroupItem, self).__init__()
        if parent is None:
            return
        self.id       = parent.id
        self.group_id = parent.group_id
        self.ref_key  = parent.ref_key
        self.cr_date  = str(parent.cr_date)
        self.node_id = parent.node_id
        self.link_id = parent.link_id
        self.subgroup_id = parent.subgroup_id

class ResourceGroup(HydraComplexModel):
    """
       - **id**          Integer(default=None)
       - **network_id**  Integer(default=None)
       - **name**        Unicode(default=None)
       - **description** Unicode(min_occurs=1, default="")
       - **status**      Unicode(default='A** pattern="[AX]")
       - **attributes**  SpyneArray(ResourceAttr)
       - **types**       SpyneArray(TypeSummary)
       - **cr_date**     Unicode(default=None)
    """
    _type_info = [
        ('id',          Integer(default=None)),
        ('network_id',  Integer(default=None)),
        ('name',        Unicode(default=None)),
        ('description', Unicode(min_occurs=0, default="")),
        ('status',      Unicode(default='A', pattern="[AX]")),
        ('attributes',  SpyneArray(ResourceAttr)),
        ('types',       SpyneArray(TypeSummary)),
        ('cr_date',     Unicode(default=None)),
    ]

    def __init__(self, parent=None, include_attributes=True):
        super(ResourceGroup, self).__init__()

        if parent is None:
            return

        self.name        = parent.name
        self.id          = parent.id
        self.description = parent.description
        self.status      = parent.status
        self.network_id  = parent.network_id
        self.cr_date     = str(parent.cr_date)

        self.types       = [TypeSummary(t) for t in parent.types]

        if include_attributes is True:
            self.attributes  = [ResourceAttr(a) for a in parent.attributes]

class Scenario(Resource):
    """
       - **id**                   Integer(default=None)
       - **name**                 Unicode(default=None)
       - **description**          Unicode(min_occurs=1, default="")
       - **network_id**           Integer(default=None)
       - **layout**               AnyDict(min_occurs=0, max_occurs=1, default=None)
       - **status**               Unicode(default='A** pattern="[AX]")
       - **locked**               Unicode(default='N** pattern="[YN]")
       - **start_time**           Unicode(default=None)
       - **end_time**             Unicode(default=None)
       - **created_by**           Integer(default=None)
       - **cr_date**              Unicode(default=None)
       - **time_step**            Unicode(default=None)
       - **resourcescenarios**    SpyneArray(ResourceScenario, default=None)
       - **resourcegroupitems**   SpyneArray(ResourceGroupItem, default=None)
    """
    _type_info = [
        ('id',                   Integer(default=None)),
        ('name',                 Unicode(default=None)),
        ('description',          Unicode(min_occurs=0, default="")),
        ('network_id',           Integer(default=None)),
        ('layout',               AnyDict(min_occurs=0, max_occurs=1, default=None)),
        ('status',               Unicode(default='A', pattern="[AX]")),
        ('locked',               Unicode(default='N', pattern="[YN]")),
        ('start_time',           Unicode(default=None)),
        ('end_time',             Unicode(default=None)),
        ('created_by',           Integer(default=None)),
        ('cr_date',              Unicode(default=None)),
        ('time_step',            Unicode(default=None)),
        ('resourcescenarios',    SpyneArray(ResourceScenario, default=None)),
        ('resourcegroupitems',   SpyneArray(ResourceGroupItem, default=None)),
    ]

    def __init__(self, parent=None, include_data=True, include_group_items=True):
        super(Scenario, self).__init__()

        if parent is None:
            return
        self.id = parent.id
        self.name = parent.name
        self.description = parent.description
        self.layout = self.get_outgoing_layout(parent.layout)
        self.network_id = parent.network_id
        self.status = parent.status
        self.locked = parent.locked
        self.start_time = parent.start_time
        self.end_time = parent.end_time
        self.time_step = parent.time_step
        self.created_by = parent.created_by
        self.cr_date = str(parent.cr_date)

        if include_data is True:
            self.resourcescenarios = [ResourceScenario(rs) for rs in parent.resourcescenarios]
        else:
            self.resourcescenarios = []

        if include_group_items is True:
            self.resourcegroupitems = [ResourceGroupItem(rgi) for rgi in parent.resourcegroupitems]
        else:
            self.resourcegroupitems = []

class RuleTypeDefinition(HydraComplexModel):
    """
       - **name**   Unicode
       - **code**   Unicode
    """
    _type_info = [
        ('name', Unicode),
        ('code', Unicode),
    ]

    def __init__(self, parent=None):
        super(RuleTypeDefinition, self).__init__()

        if parent is None:
            return

        self.name = parent.name
        self.code = parent.code

class RuleTypeLink(HydraComplexModel):
    """
       - **name**   Unicode
       - **code**   Unicode
    """
    _type_info = [
        ('rule_id', Integer),
        ('code', Unicode),
    ]

    def __init__(self, parent=None):
        super(RuleTypeLink, self).__init__()

        if parent is None:
            return

        self.rul_id = parent.rule_id
        self.code = parent.code

class RuleOwner(HydraComplexModel):
    """
       - **rule_id**   Integer
       - **user_id**    Integer
       - **edit**       Unicode
       - **view**       Unicode,
       - **cr_date**    Unicode(default=None)
       - **updated_at** Unicode(default=None)
       - **updated_by** Integer
       - **created_by** Integer
    """
    _type_info = [
        ('rule_id', Integer),
        ('user_id', Integer),
        ('edit', Unicode),
        ('view', Unicode),
        ('cr_date', Unicode),
        ('updated_at', Unicode),
        ('updated_by', Integer),
        ('created_by', Integer),
    ]
    def __init__(self, parent=None):
        super(RuleOwner, self).__init__()

        if parent is None:
            return
        self.rule_id = parent.rule_id
        self.user_id = parent.user_id
        self.edit = parent.edit
        self.view = parent.view
        self.cr_date = parent.cr_date
        self.updated_at = parent.updated_at
        self.updated_by = parent.updated_by
        self.created_by = parent.created_by

class Rule(HydraComplexModel):
    """
       - **id** Integer
       - **name** Unicode
       - **description** Unicode
       - **scenario_id** Integer
       - **ref_key** Unicode
       - **ref_id** Integer
       - **value** Unicode
       - **types** RuleTypeLink Array
       - **cr_date** Unicode(default=None)
    """
    _type_info = [
        ('id', Integer),
        ('name', Unicode),
        ('description', Unicode),
        ('scenario_id', Integer),
        ('project_id', Integer),
        ('ref_key', Unicode),
        ('ref_id', Integer),
        ('network_id', Integer),
        ('project_id', Integer),
        ('template_id', Integer),
        ('format', Unicode(default='text')),
        ('status', Unicode(default='A', pattern="[ASXD]")),
        ('value', Unicode),
        ('types', SpyneArray(AnyDict)),
        ('owners', SpyneArray(AnyDict)),
        ('cr_date', Unicode(default=None)),
    ]

    def __init__(self, parent=None):
        super(Rule, self).__init__()
        if parent is None:
            return

        self.id = parent.id
        self.name = parent.name
        self.description = parent.description
        self.ref_key = parent.ref_key
        self.ref_id = parent.network_id
        self.network_id=parent.network_id
        self.project_id=parent.project_id
        self.template_id=parent.template_id
        self.value = parent.value
        self.cr_date = str(parent.cr_date)
        self.types = [JSONObject(t) for t in parent.types]
        self.owners = [JSONObject(t) for t in parent.owners]

class Note(HydraComplexModel):
    """
       - **id** Integer
       - **ref_key** Unicode
       - **ref_id** Integer
       - **value** Unicode
       - **created_by** Integer
       - **cr_date** Unicode
    """
    _type_info = [
        ('id', Integer),
        ('ref_key', Unicode),
        ('ref_id', Integer),
        ('value', Unicode),
        ('created_by', Integer),
        ('cr_date', Unicode),
    ]

    def __init__(self, parent=None):
        super(Note, self).__init__()
        if parent is None:
            return

        self.id = parent.id
        self.ref_key = parent.ref_key
        if self.ref_key == 'NETWORK':
            self.ref_id = parent.network_id
        elif self.ref_key == 'NODE':
            self.ref_id = parent.node_id
        elif self.ref_key == 'LINK':
            self.ref_id = parent.link_id
        elif self.ref_key == 'GROUP':
            self.ref_id = parent.group_id
        elif self.ref_key == 'SCENARIO':
            self.ref_id = parent.scenario_id
        elif self.ref_key == 'PROJECT':
            self.ref_id = parent.project_id

        self.value        = parent.value
        self.created_by  = parent.created_by
        self.cr_date     = str(parent.cr_date)


class ResourceGroupDiff(HydraComplexModel):
    """
      - **scenario_1_items** SpyneArray(ResourceGroupItem)
      - **scenario_2_items** SpyneArray(ResourceGroupItem))
    """
    _type_info = [
       ('scenario_1_items', SpyneArray(ResourceGroupItem)),
       ('scenario_2_items', SpyneArray(ResourceGroupItem))
    ]

    def __init__(self, parent=None):
        super(ResourceGroupDiff, self).__init__()

        if parent is None:
            return

        self.scenario_1_items = [ResourceGroupItem(rs) for rs in parent['scenario_1_items']]
        self.scenario_2_items = [ResourceGroupItem(rs) for rs in parent['scenario_2_items']]

class ResourceScenarioDiff(HydraComplexModel):
    """
       - **resource_attr_id**     Integer(default=None)
       - **scenario_1_dataset**   Dataset
       - **scenario_2_dataset**   Dataset
    """
    _type_info = [
        ('resource_attr_id',     Integer(default=None)),
        ('scenario_1_dataset',   Dataset),
        ('scenario_2_dataset',   Dataset),
    ]

    def __init__(self, parent=None):
        super(ResourceScenarioDiff, self).__init__()

        if parent is None:
            return

        self.resource_attr_id   = parent['resource_attr_id']

        self.scenario_1_dataset = Dataset(parent['scenario_1_dataset'])
        self.scenario_2_dataset = Dataset(parent['scenario_2_dataset'])

class ScenarioDiff(HydraComplexModel):
    """
       - **resourcescenarios**    SpyneArray(ResourceScenarioDiff)
       - **groups**               ResourceGroupDiff
    """
    _type_info = [
        ('resourcescenarios',    SpyneArray(ResourceScenarioDiff)),
        ('groups',               ResourceGroupDiff),
    ]

    def __init__(self, parent=None):
        super(ScenarioDiff, self).__init__()

        if parent is None:
            return

        self.resourcescenarios = [ResourceScenarioDiff(rd) for rd in parent['resourcescenarios']]
        self.groups = ResourceGroupDiff(parent['groups'])

class NetworkOwner(HydraComplexModel):
    """
       - **network_id**   Integer
       - **user_id**  Integer
       - **edit**     Unicode
       - **view**     Unicode
        - **cr_date**   Unicode(default=None)
       - **updated_at** Unicode(default=None)
       - **updated_by** Integer
       - **created_by** Integer
    """
    _type_info = [
        ('network_id',   Integer),
        ('user_id',  Integer),
        ('edit',     Unicode),
        ('view',     Unicode),
        ('cr_date', Unicode),
        ('updated_at', Unicode),
        ('updated_by', Integer),
        ('created_by', Integer),
    ]
    def __init__(self, parent=None):
        super(NetworkOwner, self).__init__()

        if parent is None:
            return
        self.network_id = parent.network_id
        self.user_id    = parent.user_id
        self.edit       = parent.edit
        self.view       = parent.view

        self.cr_date = parent.cr_date
        self.updated_at = parent.updated_at
        self.updated_by = parent.updated_by
        self.created_by = parent.created_by

class Network(Resource):
    """
       - **project_id**          Integer(default=None)
       - **id**                  Integer(default=None)
       - **name**                Unicode(default=None)
       - **description**         Unicode(min_occurs=1, default=None)
       - **created_by**          Integer(default=None)
       - **cr_date**             Unicode(default=None)
       - **layout**              AnyDict(min_occurs=0, max_occurs=1, default=None)
       - **appdata**             AnyDict(min_occurs=0, max_occurs=1, default=None)
       - **status**              Unicode(default='A')
       - **attributes**          SpyneArray(ResourceAttr)
       - **scenarios**           SpyneArray(Scenario)
       - **nodes**               SpyneArray(Node)
       - **links**               SpyneArray(Link)
       - **owners**              SpyneArray(Owners)
       - **resourcegroups**      SpyneArray(ResourceGroup)
       - **types**               SpyneArray(TypeSummary)
       - **projection**          Unicode(default=None)
    """
    _type_info = [
        ('project_id', Integer(default=None)),
        ('id', Integer(default=None)),
        ('name', Unicode(default=None)),
        ('description', Unicode(min_occurs=0, default=None)),
        ('created_by', Integer(default=None)),
        ('cr_date', Unicode(default=None)),
        ('layout', AnyDict(min_occurs=0, max_occurs=1, default=None)),
        ('appdata', AnyDict(min_occurs=0, max_occurs=1, default=None)),
        ('status', Unicode(default='A', pattern="[AX]")),
        ('attributes', SpyneArray(ResourceAttr)),
        ('scenarios', SpyneArray(Scenario)),
        ('nodes', SpyneArray(Node)),
        ('links', SpyneArray(Link)),
        ('resourcegroups', SpyneArray(ResourceGroup)),
        ('owners', SpyneArray(NetworkOwner)),
        ('types', SpyneArray(TypeSummary)),
        ('projection', Unicode(default=None)),
    ]

    def __init__(self, parent=None, include_attributes=True, include_data=True):
        super(Network, self).__init__()

        if parent is None:
            return
        self.project_id = parent.project_id
        self.id = parent.id
        self.name = parent.name
        self.description = parent.description
        self.created_by = parent.created_by
        self.cr_date = str(parent.cr_date)
        self.layout = self.get_outgoing_layout(parent.layout)
        self.appdata = self.get_outgoing_layout(parent.appdata)
        self.status = parent.status
        self.scenarios = [Scenario(s, include_data=include_data, include_group_items=include_data) for s in parent.scenarios]
        self.nodes = [Node(n, include_attributes) for n in parent.nodes]
        self.links = [Link(l, include_attributes) for l in parent.links]
        self.resourcegroups = [ResourceGroup(rg, include_attributes) for rg in parent.resourcegroups]
        self.types = [TypeSummary(t) for t in parent.types]
        self.owners = [NetworkOwner(o) for o in parent.owners]
        self.projection = parent.projection

        if include_attributes:
            self.attributes = [ResourceAttr(ra) for ra in parent.attributes]

class NetworkExtents(HydraComplexModel):
    """
       - **network_id** Integer(default=None)
       - **min_x**      Decimal(default=0)
       - **min_y**      Decimal(default=0)
       - **max_x**      Decimal(default=0)
       - **max_y**      Decimal(default=0)
    """
    _type_info = [
        ('network_id', Integer(default=None)),
        ('min_x',      Decimal(default=0)),
        ('min_y',      Decimal(default=0)),
        ('max_x',      Decimal(default=0)),
        ('max_y',      Decimal(default=0)),
    ]

    def __init__(self, parent=None):
        super(NetworkExtents, self).__init__()

        if parent is None:
            return

        self.network_id = parent.network_id
        self.min_x = parent.min_x
        self.min_y = parent.min_y
        self.max_x = parent.max_x
        self.max_y = parent.max_y

class Project(Resource):
    """
   - **id**          Integer(default=None)
   - **name**        Unicode(default=None)
   - **description** Unicode(default=None)
   - **status**      Unicode(default='A')
   - **cr_date**     Unicode(default=None)
   - **created_by**  Integer(default=None)
   - **appdata**     AnyDict(default=None)
   - **attributes**  SpyneArray(ResourceAttr)
   - **attribute_data** SpyneArray(ResourceScenario)
    """
    _type_info = [
        ('id',          Integer(default=None)),
        ('name',        Unicode(default=None)),
        ('description', Unicode(default=None)),
        ('status',      Unicode(default='A', pattern="[AX]")),
        ('cr_date',     Unicode(default=None)),
        ('created_by',  Integer(default=None)),
        ('appdata',     AnyDict(min_occurs=0, max_occurs=1, default=None)),
        ('attributes',  SpyneArray(ResourceAttr)),
        ('attribute_data', SpyneArray(ResourceScenario)),
    ]

    def __init__(self, parent=None):
        super(Project, self).__init__()

        if parent is None:
            return

        self.id          = parent.id
        self.name        = parent.name
        self.description = parent.description
        self.status      = parent.status
        self.cr_date     = str(parent.cr_date)
        self.created_by  = parent.created_by

        #this is a failsafe to ensure that the 'appdata' column
        #is processed correctly, as it is a JSON column type which may
        #not work with with serialising data.
        appdata = {}
        if parent.appdata is not None:
            for k, v in parent.appdata.items():
                appdata[k] = v
        self.appdata = appdata

        self.attributes  = [ResourceAttr(ra) for ra in parent.attributes]
        self.attribute_data  = [ResourceScenario(rs) for rs in parent.attribute_data]

class ProjectSummary(Resource):
    """
       - **id**          Integer(default=None)
       - **name**        Unicode(default=None)
       - **description** Unicode(default=None)
       - **status**      Unicode(default=None)
       - **cr_date**     Unicode(default=None)
       - **created_by**  Integer(default=None)
    """
    _type_info = [
        ('id',          Integer(default=None)),
        ('name',        Unicode(default=None)),
        ('description', Unicode(default=None)),
        ('status',      Unicode(default=None)),
        ('cr_date',     Unicode(default=None)),
        ('created_by',  Integer(default=None)),
    ]

    def __init__(self, parent=None):
        super(ProjectSummary, self).__init__()

        if parent is None:
            return
        self.id          = parent.id
        self.name        = parent.name
        self.description = parent.description
        self.cr_date = str(parent.cr_date)
        self.created_by = parent.created_by
        self.summary    = parent.summary
        self.status     = parent.status

class User(HydraComplexModel):
    """
       - **id**  Integer
       - **username** Unicode(default=None)
       - **display_name** Unicode(default=None)
       - **password** Unicode(default=None)
    """
    _type_info = [
        ('id',  Integer),
        ('username', Unicode(default=None)),
        ('display_name', Unicode(default=None)),
        ('password', Unicode(default=None)),
    ]

    def __init__(self, parent=None):
        super(User, self).__init__()

        if parent is None:
            return

        self.id = parent.id
        self.username = parent.username
        self.display_name = parent.display_name
        if isinstance(parent.password, bytes):
            self.password = parent.password.decode("utf-8")
        else:
            self.password = parent.password

class Perm(HydraComplexModel):
    """
       - **id**   Integer
       - **name** Unicode
       - **code** Unicode
    """
    _type_info = [
        ('id',   Integer),
        ('name', Unicode),
        ('code', Unicode),
    ]

    def __init__(self, parent=None):
        super(Perm, self).__init__()

        if parent is None:
            return

        self.id   = parent.id
        self.name = parent.name
        self.code = parent.code

class RoleUser(HydraComplexModel):
    """
       - **user_id**  Integer
    """
    _type_info = [
        ('user_id',  Integer),
    ]
    def __init__(self, parent=None):
        super(RoleUser, self).__init__()

        if parent is None:
            return

        self.user_id = parent.user.id

class RolePerm(HydraComplexModel):
    """
       - **perm_id**   Integer
    """
    _type_info = [
        ('perm_id',   Integer),
    ]

    def __init__(self, parent=None):
        super(RolePerm, self).__init__()

        if parent is None:
            return

        self.perm_id = parent.perm_id

class Role(HydraComplexModel):
    """
       - **id**     Integer
       - **name**   Unicode
       - **code**   Unicode
       - **roleperms** SpyneArray(RolePerm)
       - **roleusers** SpyneArray(RoleUser)
    """
    _type_info = [
        ('id',     Integer),
        ('name',   Unicode),
        ('code',   Unicode),
        ('roleperms', SpyneArray(RolePerm)),
        ('roleusers', SpyneArray(RoleUser)),
    ]

    def __init__(self, parent=None):
        super(Role, self).__init__()

        if parent is None:
            return

        self.id = parent.id
        self.name = parent.name
        self.code = parent.code
        self.roleperms = [RolePerm(rp) for rp in parent.roleperms]
        self.roleusers = [RoleUser(ru) for ru in parent.roleusers]

class PluginParam(HydraComplexModel):
    """
       - **name**        Unicode
       - **value**       Unicode
    """
    _type_info = [
        ('name',        Unicode),
        ('value',       Unicode),
    ]

    def __init__(self, parent=None):
        super(PluginParam, self).__init__()

        if parent is None:
            return

        self.name = parent.name
        self.value = parent.value


class Plugin(HydraComplexModel):
    """
       - **name**        Unicode
       - **location**    Unicode
       - **params**      SpyneArray(PluginParam)
    """
    _type_info = [
        ('name',        Unicode),
        ('location',    Unicode),
        ('params',      SpyneArray(PluginParam)),
    ]

    def __init__(self, parent=None):
        super(Plugin, self).__init__()

        if parent is None:
            return

        self.name = parent.name
        self.location = parent.location
        self.params = [PluginParam(pp) for pp in parent.params]


class ProjectOwner(HydraComplexModel):
    """
       - **project_id**   Integer
       - **user_id**    Integer
       - **edit**       Unicode
       - **view**       Unicode
       - **cr_date**    Unicode(default=None)
       - **updated_at** Unicode(default=None)
       - **updated_by** Integer
       - **created_by** Integer
    """
    _type_info = [
        ('project_id',   Integer),
        ('user_id',  Integer),
        ('edit',     Unicode),
        ('view',     Unicode)
        ('cr_date', Unicode),
        ('updated_at', Unicode),
        ('updated_by', Integer),
        ('created_by', Integer),
    ]
    def __init__(self, parent=None):
        super(ProjectOwner, self).__init__()

        if parent is None:
            return
        self.project_id = parent.project_id
        self.user_id    = parent.user_id
        self.edit       = parent.edit
        self.view       = parent.view
        self.cr_date = parent.cr_date
        self.updated_at = parent.updated_at
        self.updated_by = parent.updated_by
        self.created_by = parent.created_by

class DatasetOwner(HydraComplexModel):
    """
       - **dataset_id**   Integer
       - **user_id**    Integer
       - **edit**       Unicode
       - **view**       Unicode
       - **cr_date**    Unicode(default=None)
       - **updated_at** Unicode(default=None)
       - **updated_by** Integer
       - **created_by** Integer
    """
    _type_info = [
        ('dataset_id',   Integer),
        ('user_id',  Integer),
        ('edit',     Unicode),
        ('view',     Unicode),
        ('cr_date', Unicode),
        ('updated_at', Unicode),
        ('updated_by', Integer),
        ('created_by', Integer),
    ]
    def __init__(self, parent=None):
        super(DatasetOwner, self).__init__()

        if parent is None:
            return
        self.dataset_id = parent.dataset_id
        self.user_id    = parent.user_id
        self.edit       = parent.edit
        self.view       = parent.view
        self.cr_date = parent.cr_date
        self.updated_at = parent.updated_at
        self.updated_by = parent.updated_by
        self.created_by = parent.created_by

class Unit(HydraComplexModel):
    """
       - **name** Unicode
       - **abbr** Unicode
       - **abbreviation** Unicode
       - **cf** Double
       - **lf** Double
       - **info** Unicode
       - **description** Unicode
       - **dimension_id** Integer
       - **project_id** Integer
    """
    _type_info = [
        ('id',     Integer),
        ('name', Unicode),
        ('abbr', Unicode),  # Alias for abbreviation
        ('abbreviation', Unicode),
        ('cf', Double),
        ('lf', Double),
        ('info', Unicode), # Alias for description
        ('description', Unicode),
        #''('dimension', Unicode),
        ('dimension_id', Integer),
        ('project_id', Integer)
    ]

    def __init__(self, parent=None):
        super(Unit, self).__init__()

        if parent is None:
            return
        self.id = parent.id
        self.name = parent.name
        self.abbr = parent.abbreviation
        self.abbreviation = parent.abbreviation
        self.cf   = parent.cf
        self.lf   = parent.lf
        self.info = parent.description
        self.description = parent.description
        self.dimension_id = parent.dimension_id
        self.project_id = parent.project_id

class Dimension(HydraComplexModel):
    """
        A dimension, with name and units
       - **name** Unicode
       - **units** SpyneArray(Unicode)
       - **description** Unicode
       - **project_id** Integer
    """
    _type_info = [
        ('id', Integer),
        ('name', Unicode),
        ('description', Unicode),
        ('units', SpyneArray(Unit)),
        ('project_id', Integer)
    ]

    def __init__(self, parent=None):
        if parent is None:
            return
        self.id = parent.id
        self.name = parent.name
        self.units = [Unit(u) for u in parent.units]
        self.description = parent.description
        self.project_id = parent.project_id
