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
from spyne.decorator import rpc
from spyne.model.primitive import Integer, Unicode, AnyDict
from spyne.model.complex import Array as SpyneArray
from .complexmodels import Project,\
ProjectSummary,\
ResourceScenario,\
ResourceSummary,\
Network
from .service import HydraService
from hydra_base.lib import project as project_lib
from hydra_base.lib.objects import JSONObject

class ProjectService(HydraService):
    """
        The project SOAP service
    """

    @rpc(Project, _returns=Project)
    def add_project(ctx, project):
        """
            Add a new project

            Args:
                project (complexmodels.Project): The new project to be added.
                                                 The project does not include networks.

            Returns:
                complexmodels.Project: The project received, but with an ID this time.


            Raises:

        """
        new_proj = project_lib.add_project(project, **ctx.in_header.__dict__)
        ret_proj = Project(new_proj)
        return ret_proj

    @rpc(Project, _returns=Project)
    def update_project(ctx, project):
        """
            Update a project

            Args:
                project (complexmodels.Project): The project to be updated.
                    All the attributes of this project will be used to update
                     the existing project
            Returns:
                complexmodels.Project: The updated project

            Raises:
                ResourceNotFoundError: If the project is not found.

        """
        proj_i = project_lib.update_project(project, **ctx.in_header.__dict__)

        return Project(proj_i)


    @rpc(Integer, _returns=AnyDict)
    def get_project(ctx, project_id):
        """
        Get an existing Project

        Args:
            project_id (int): The ID of the project to retrieve

        Returns:
            complexmodels.Project: The requested project

        Raises:
            ResourceNotFoundError: If the project is not found.
        """

        proj_dict = project_lib.get_project(project_id, **ctx.in_header.__dict__)

        return JSONObject(proj_dict)


    @rpc(Integer, _returns=SpyneArray(AnyDict))
    def get_project_hierarchy(ctx, project_id):
        """
        Return a list of project-ids which represent the links in the chain up to the root project
        [project_id, parent_id, parent_parent_id ...etc]
        If the project has no parent, return [project_id]

        Args:
            project_id (int): The ID of the project to retrieve

        Returns:
            Array(complexmodels.AnyDict): A list of the projects in the hierarchy (just the top level result)

        Raises:
            ResourceNotFoundError: If the project is not found.
        """

        #This returns a list of JSONObjects
        proj_dicts = project_lib.get_project_hierarchy(project_id, **ctx.in_header.__dict__)

        return proj_dicts


    @rpc(Integer, _returns=SpyneArray(ResourceScenario))
    def get_project_attribute_data(ctx, project_id):
        """
        Get the data for a project
        Args:
            project_id (int): THe ID of the project
        Returns
            list(complexmodels.ResourceScenario)

        Raises:
            ResourceNotFoundError: If the project is not found.
        """

        project_data = project_lib.get_project_attribute_data(project_id,
                                                              **ctx.in_header.__dict__)
        return [ResourceScenario(rs) for rs in project_data]

    @rpc(Unicode, _returns=SpyneArray(Project))
    def get_project_by_name(ctx, project_name):
        """
        If you don't know the ID of the project in question, but do know
        the name, use this function to retrieve it. A project name must be unique
        to a user, but a user can have access to another user's project with the
        same name, so this function returns a list

        Args:
            project_name (string): The name of the project to retrieve

        Returns:
            list(complexmodels.Project): The requested project. More than one
            project can be returned, as a user can have a project shared with them
            which as the same name as a projec they are the owner of.

        Raises:
            ResourceNotFoundError: If the project is not found.

        """
        proj_dicts = project_lib.get_project_by_name(project_name, **ctx.in_header.__dict__)

        return [Project(proj_dict) for proj_dict in proj_dicts]

    @rpc(Integer, _returns=SpyneArray(ProjectSummary))
    def get_projects(ctx, user_id):
        """
        Get all the projects belonging to a user.

        Args:
            user_id (int): The user ID whose projects you want

        Returns:
            List(complexmodels.Project): The requested projects

        Raises:
            ResourceNotFoundError: If the User is not found.

        """
        if user_id is None:
            user_id = ctx.in_header.user_id
        project_dicts = project_lib.get_projects(user_id, **ctx.in_header.__dict__)
        projects = [Project(p) for p in project_dicts]
        return projects

    @rpc(Integer, Unicode(pattern="[AX]"), _returns=Unicode)
    def set_project_status(ctx, project_id, status):
        """
        Set the status of a project to 'A' or 'X'. A project with status 'X'
        will not appear in 'get_projects' calls, and must be retrieved explicitly

        Args:
            project_id (int): The ID of the project to change.
            status (char): A or X (Active or Deleted)

        Returns:
            string: 'OK'

        Raises:
            ResourceNotFoundError: If the Project is not found.

        """
        project_lib.set_project_status(project_id, status, **ctx.in_header.__dict__)
        return 'OK'

    @rpc(Integer, _returns=Unicode)
    def delete_project(ctx, project_id):
        """
        Delete a project from the DB completely. WARNING: THIS WILL DELETE ALL
        THE PROJECT'S NETWORKS AND CANNOT BE REVERSED!

        Args:
            project_id (int): The ID of the project to purge.

        Returns:
            string: 'OK'

        Raises:
            ResourceNotFoundError: If the Project is not found.
        """
        project_lib.delete_project(project_id, **ctx.in_header.__dict__)
        return 'OK'

    @rpc(Integer, Unicode(pattern="[YN]", default='N'), _returns=SpyneArray(ResourceSummary))
    def get_networks(ctx, project_id, include_data):
        """
        Get all networks in a project

        Args:
            project_id (int): The ID of the project whose networks you want.
            include_data (string) ('Y' or 'N'): Include data with the networks?
                Defaults as 'Y' but using 'N' gives a significant performance boost.

        Returns:
            List(complexmodels.Network): All the project's Networks.

        Raises:
            ResourceNotFoundError: If the Project is not found.

        """

        net_dicts = project_lib.get_networks(
            project_id,
            include_data=False,
            **ctx.in_header.__dict__)

        networks = [ResourceSummary(n, include_attributes=False) for n in net_dicts]

        return networks

    @rpc(Integer, _returns=Project)
    def get_network_project(ctx, network_id):
        """
        Get the project of a specified network

        Args:
            network_id (int): The ID of the network whose project details you want

        Returns:
            complexmodels.Project: The parent project of the specified Network

        Raises:
            ResourceNotFoundError: If the Network is not found.


        """
        proj = project_lib.get_network_project(
            network_id,
            **ctx.in_header.__dict__)

        return Project(proj)

    @rpc(Integer,
         Integer,
         Unicode(default=None),
         Unicode(Default=None),
         _returns=Integer)
    def clone_project(ctx, project_id, recipient_user_id, new_project_name, new_project_description):
        """
            Create an exact clone of the specified project for the specified user.
        """
        new_project_id = project_lib.clone_project(project_id,
                                               recipient_user_id,
                                               new_project_name,
                                               new_project_description,
                                               **ctx.in_header.__dict__)
        return new_project_id


    @rpc(Integer,
         _returns=Project)
    def get_project_by_network_id(ctx, network_id):
        """
            Get a project from the ID of a network in it.
        """
        proj_i = project_lib.get_project_by_network_id(network_id,
                                               **ctx.in_header.__dict__)
        return Project(proj_i)
