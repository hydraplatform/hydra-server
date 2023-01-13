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
from spyne.model.primitive import Integer, Unicode, AnyDict
from spyne.model.complex import Array as SpyneArray
from spyne.decorator import rpc
from .complexmodels import Rule, RuleTypeLink, RuleTypeDefinition
from hydra_base.lib import rules

from .service import HydraService

class RuleService(HydraService):

    """
        The data SOAP service
    """

    @rpc(Integer, _returns=SpyneArray(Rule))
    def get_rules(ctx, scenario_id):
        """
            Get all the rules in a scenario
        """
        scenario_rules = rules.get_rules(scenario_id, **ctx.in_header.__dict__)
        return [Rule(r) for r in scenario_rules]

    @rpc(Integer, _returns=Rule)
    def get_rule(ctx, rule_id):
        """
            Get an individual role by its ID.
        """
        rule_i = rules.get_rule(rule_id, **ctx.in_header.__dict__)
        return Rule(rule_i)

    @rpc(Rule, Unicode(default='Y', pattern='[YN]'), _returns=Rule)
    def add_rule(ctx, rule, include_network_users='Y'):
        """
            Add a rule to a given scenario
        """

        if include_network_users == 'Y':
            include_network_users = True
        else:
            include_network_users = False

        rule_i = rules.add_rule(rule, include_network_users=include_network_users, **ctx.in_header.__dict__)

        return Rule(rule_i)

    @rpc(SpyneArray(Rule), _returns=SpyneArray(Rule))
    def add_rules(ctx, rule_list):
        """
            Add a rule to a given scenario
        """
        returned_rules = []
        for rule in rule_list:
            rule_i = rules.add_rule(rule, **ctx.in_header.__dict__)
            returned_rules.append(Rule(rule_i))

        return returned_rules

    @rpc(Rule, _returns=Rule)
    def update_rule(ctx, rule):
        """
            Update a rule. Ensure that scenario_id is specified in the rule.
        """
        rule_i = rules.update_rule(rule, **ctx.in_header.__dict__)
        return Rule(rule_i)

    @rpc(Integer, _returns=Unicode)
    def delete_rule(ctx, rule_id):
        """
            Set the status of a rule to inactive, so it will be excluded when
            'get_rules' is called.
        """
        rules.delete_rule(rule_id, **ctx.in_header.__dict__)
        return 'OK'

    @rpc(Integer, _returns=Unicode)
    def activate_rule(ctx, rule_id):
        """
            Set the status of a rule to active, so it will be included when
            'get_rules' is called.
        """
        rules.activate_rule(rule_id, **ctx.in_header.__dict__)
        return 'OK'

    @rpc(Integer, _returns=Unicode)
    def purge_rule(ctx, rule_id):
        """
            Remove a rule permanently
        """
        rules.purge_rule(rule_id, **ctx.in_header.__dict__)
        return 'OK'

    @rpc(Unicode,
         Integer,
         Integer,
         _returns=SpyneArray(Rule))
    def get_resource_rules(ctx, ref_key, ref_id, scenario_id=None, **kwargs):
        """
            Get all the rules for a given resource.
            Args:
                ref_key (string): NETWORK, NODE, LINK, GROUP
                ref_id (int): ID of the resource
                scenario_id (int): Optional which filters on scenario ID also
            Returns:
                List of Rule SQLAlchemy objects
        """
        rules_i = rules.get_resource_rules(ref_key, ref_id, scenario_id, **ctx.in_header.__dict__)

        return [Rule(r) for r in rules_i]

    @rpc(RuleTypeDefinition,
         _returns=RuleTypeDefinition)
    def add_rule_type_definition(ctx, ruletypedefinition, **kwargs):
        """
            Add a rule type definition
            Args:
                ruletypedefinition (Spyne or JSONObject object). This looks like:
                                    {
                                      'name': 'My Rule Type',
                                      'code': 'my_rule_type'
                                    }
            Returns:
                ruletype_i (SQLAlchemy ORM Object) new rule type from DB
        """
        new_rtd = rules.add_rule_type_definition(ruletypedefinition, **ctx.in_header.__dict__)

        return RuleTypeDefinition(new_rtd)

    @rpc(Unicode, Integer(default=None), _returns=SpyneArray(Rule))
    def get_rules_of_type(ctx, typecode, scenario_id=None, **kwargs):
        rules_of_type = rules.get_rules_of_type(typecode, scenario_id=scenario_id, **ctx.in_header.__dict__)
        return [Rule(rot) for rot in rules_of_type]

    @rpc(_returns=SpyneArray(RuleTypeDefinition))
    def get_rule_type_definitions(ctx, **kwargs):
        """
            Get all rule type definitions
        """
        rule_type_defs = rules.get_rule_type_definitions(**ctx.in_header.__dict__)
        return [RuleTypeDefinition(rtd) for rtd in rule_type_defs]

    @rpc(Unicode,
         _returns=RuleTypeDefinition)
    def get_rule_type_definition(ctx, typecode, **kwargs):
        """
            Get a rule type definition by its code
        """
        rule_type_def = rules.get_rule_type_definition(typecode, **ctx.in_header.__dict__)
        return RuleTypeDefinition(rule_type_def)

    @rpc(Unicode,
     _returns=RuleTypeDefinition)
    def purge_rule_type_definition(ctx, typecode, **kwargs):
        """
            Delete a rule type from the DB. Doing this will revert all existing rules to
            having no type (rather than deleting them)
            args:
                typecode: Type definitions do not used IDs, rather codes. This is to code to purge
            returns:
                 'OK'
            raises:
                ResourceNotFoundError if the rule type definintion code does not exist
        """
        rules.purge_rule_type_definition(typecode, **ctx.in_header.__dict__)
        return 'OK'

    @rpc(Integer,
     _returns=SpyneArray(Rule))
    def get_scenario_rules(ctx, scenario_id, **kwargs):
        """
            Get all the rules for a given scenario.
        """
        scenario_rules = rules.get_scenario_rules(scenario_id, **ctx.in_header.__dict__)
        return [Rule(r) for r in scenario_rules]

    @rpc(Integer,
         Unicode(default=None),
         Integer(default=None),
         AnyDict(default={}),
         _returns=Rule)
    def clone_rule(ctx, rule_id, target_ref_key=None, target_ref_id=None, scenario_id_map=None, **kwargs):
        """
            Clone a rule
            args:
                rule_id (int): The rule to clone
                target_ref_key (string): If the rule is to be cloned into a different
                                         resource, specify the new resources type
                target_ref_id (int): If the rule is to be cloned into a
                                     different resources, specify the resource ID.
                scenario_id_map (dict): If the old rule is specified in a scenario,
                                        then provide a dictionary mapping from the
                                        old scenario ID to the new one, like {123 : 456}
            Cloning will only occur into a different resource if both ref_key AND
            ref_id are provided. Otherwise it will maintain its original ref_key and ref_id.

            return:
                SQLAlchemy ORM object
        """

        #deal with spynes inability to handle default dicts
        if scenario_id_map is None:
            scenario_id_map = {}

        newrule = rules.clone_rule(rule_id,
                                   target_ref_key=target_ref_key,
                                   target_ref_id=target_ref_id,
                                   scenario_id_map=scenario_id_map,
                                   **ctx.in_header.__dict__)

        return Rule(newrule)

    @rpc(Integer,
         Unicode,
         _returns=Rule)
    def set_rule_type(ctx, rule_id, typecode, **kwargs):
        """
            Assign a rule type to a rule
            args:
                rule_id (int): THe ID of the rule to apply the type to
                typecode (string): Types do not use IDS as identifiers, rather codes.
                                   Apply the type with this code to the rule
            returns:
                The updated rule (Sqlalchemy ORM Object)
        """
        update_rule = rules.set_rule_type(rule_id,
                                          typecode,
                                          **ctx.in_header.__dict__)

        return Rule(update_rule)

    @rpc(Integer,
         Integer(default=None),
         Unicode(pattern='[YN]', default='Y'),
         _returns=SpyneArray(Rule))
    def get_network_rules(ctx, network_id, scenario_id, summary):
        """
            Get all the rules within a network -- including rules associated to
            all nodes, links and group=s.
            Args:
                network_id (int): ID of the resource
                scenario_id (int): Optional which filters on scenario ID also
            Returns:
                List of Rule Complexmodels
        """
        net_rules = rules.get_network_rules(network_id,
                                scenario_id=scenario_id,
                                summary=summary=='Y',
                                **ctx.in_header.__dict__)
        return net_rules
