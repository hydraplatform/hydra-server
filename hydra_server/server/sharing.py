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
from spyne.model.primitive import Unicode, Integer, Unicode
from spyne.decorator import rpc
from .service import HydraService
from hydra_base.lib import sharing
from .complexmodels import NetworkOwner, ProjectOwner
from spyne.model.complex import Array as SpyneArray


class SharingService(HydraService):
    """
        The network SOAP service.
    """

    @rpc(Integer, Unicode(max_occurs='unbounded'),
         Unicode(pattern="[YN]"), Unicode(pattern="[YN]", default='Y'), _returns=Unicode())
    def share_network(ctx, network_id, usernames, read_only, share):
        """

        Share a network with a list of users, identified by their usernames.

        Args:
            network_id (int): The ID of the network to share
            usernames  (List(Unicode)): THe list of usernames with whom to share the network
            read_only  (string) (Y or N): Can the users edit as well as view the network?
            share      (string) (optional) (Y or N): Can the users share the network with other users? This only goes 1 level deep, so if you share a network with a user and give them sharing ability, they cannot then set the 'share' flag to 'Y' when sharing with someone else.

        Returns:
            string: 'OK'

        Raises:
            ResourceNotFoundError: If the network is not found
            ResourceNotFoundError: If one of the usernames is incorrect or does not exist

        """

        sharing.share_network(network_id,
                              usernames,
                              read_only,
                              share,
                              **ctx.in_header.__dict__)

        return 'OK'

    @rpc(Integer, Unicode(max_occurs='unbounded'),
         Unicode(pattern="[YN]"), Unicode(pattern="[YN]"), _returns=Unicode)
    def share_project(ctx, project_id, usernames, read_only, share):
        """

        Share an entire project with a list of users, identifed by their usernames.
        All the projectt's networks will be shared also.

        Args:
            project_id (int): The ID of the project to share
            usernames  (List(Unicode)): The list of usernames with whom to share the project
            read_only  (string) (Y or N): Can the users edit as well as view the project?
            share      (string) (optional) (Y or N): Can the users share the project with other users? This only goes 1 level deep, so if you share a project with a user and give them sharing ability, they cannot then set the 'share' flag to 'Y' when sharing with someone else.

        Returns:
            string: 'OK'

        Raises:
            ResourceNotFoundError: If the project is not found
            ResourceNotFoundError: If one of the usernames is incorrect or does not exist

        """
        sharing.share_project(project_id,
                              usernames,
                              read_only,
                              share,
                              **ctx.in_header.__dict__)
        return "OK"

    @rpc(Integer, Unicode(max_occurs="unbounded"),
         Unicode(pattern="[YN]"), Unicode(pattern="[YN]"), Unicode(pattern="[YN]"),
         _returns=Unicode)
    def set_project_permission(ctx, project_id, usernames, read, write, share):
        """

        Set permissions on a project to a list of users, identifed by their usernames.
        THIS ACTION IS THEN PERFORMED ON ALL THE PROJECT'S NETWORKS!

        Args:
            project_id (int): The ID of the project to share
            usernames  (List(Unicode)): The list of usernames with whom to share the project
            read       (string) (Y or N): Can the users read the project?
            write      (string) (Y or N): Can the users edit the project?
            share      (string) (optional) (Y or N): Can the users share the project with other users? This only goes 1 level deep, so if you share a network with a user and give them sharing ability, they cannot then set the 'share' flag to 'Y' when sharing with someone else.

        Returns:
            string: 'OK'

        Raises:
            ResourceNotFoundError: If the project is not found
            ResourceNotFoundError: If one of the usernames is incorrect or does not exist

        """
        sharing.set_project_permission(project_id,
                                       usernames,
                                       read,
                                       write,
                                       share,
                                       **ctx.in_header.__dict__)

    @rpc(Integer, Unicode(max_occurs="unbounded"),
         Unicode(pattern="[YN]"), Unicode(pattern="[YN]"), Unicode(pattern="[YN]"),
         _returns=Unicode)
    def set_network_permission(ctx, network_id, usernames, read, write, share):
        """

        Set permissions on a network to a list of users, identifed by
        their usernames. The read flag ('Y' or 'N') sets read access, the write
        flag sets write access. If the read flag is 'N', then there is
        automatically no write access or share access.

        Args:
            network_id (int): The ID of the network to share
            usernames  (List(Unicode)): The list of usernames with whom to share the network
            read       (string) (Y or N): Can the users read the network?
            write      (string) (Y or N): Can the users edit the network?
            share      (string) (optional) (Y or N): Can the users share the network with other users? This only goes 1 level deep, so if you share a network with a user and give them sharing ability, they cannot then set the 'share' flag to 'Y' when sharing with someone else.

        Returns:
            string: 'OK'

        Raises:
            ResourceNotFoundError: If the network is not found
            ResourceNotFoundError: If one of the usernames is incorrect or does not exist

        """

        sharing.set_network_permission(network_id,
                                       usernames,
                                       read,
                                       write,
                                       share,
                                       **ctx.in_header.__dict__)

        return "OK"

    @rpc(Integer, Unicode(max_occurs="unbounded"),
         Unicode(pattern="[YN]"), Unicode(pattern="[YN]"), Unicode(pattern="[YN]"),
         _returns=Unicode)
    def hide_dataset(ctx, dataset_id, exceptions, read, write, share):
        """

        Hide a particular piece of data so it can only be seen by its owner.
        Only an owner can hide (and unhide) data.
        Data with no owner cannot be hidden.

        Args:
            dataset_id (int): The ID of the dataset to be hidden
            exceptions  (List(Unicode)): the usernames of those with permission to view the data
            read       (string) (Y or N): Can the users read the dataset?
            write      (string) (Y or N): Can the users edit the dataset?
            share      (string) (Y or N): Can the users share the dataset with other users? This only goes 1 level deep, so if you share a network with a user and give them sharing ability, they cannot then set the 'share' flag to 'Y' when sharing with someone else.

        Returns:
            string: 'OK'

        Raises:
            ResourceNotFoundError: If the dataset is not found
            HydraError: If the request is being made by a non-owner of the dataset

        """
        sharing.hide_dataset(dataset_id,
                             exceptions,
                             read,
                             write,
                             share,
                             **ctx.in_header.__dict__)

        return "OK"

    @rpc(Integer,
         _returns=Unicode)
    def unhide_dataset(ctx, dataset_id):
        """
        Un Hide a particular piece of data so it can only be seen by its owner.
        Only an owner can hide (and unhide) data.

        Args:
            dataset_id (int): The ID of the dataset to be un-hidden

        Returns:
            string: 'OK'

        Raises:
            ResourceNotFoundError: If the dataset is not found
            HydraError: If the request is being made by a non-owner of the dataset

        """
        sharing.unhide_dataset(dataset_id,
                             **ctx.in_header.__dict__)

        return "OK"

    @rpc(SpyneArray(Integer),
         _returns=SpyneArray(ProjectOwner))
    def get_all_project_owners(ctx, project_ids=None):
        """
            Get the project owner entries for all the requested projects.
            If the project_ids argument is None, return all the owner entries
            for ALL projects
        """
        owners = sharing.get_all_project_owners(project_ids,
                                                **ctx.in_header.__dict__)

        return [ProjectOwner(o) for o in owners]


    @rpc(SpyneArray(Integer),
         _returns=SpyneArray(NetworkOwner))
    def get_all_network_owners(ctx, network_ids=None):
        """
            Get the network owner entries for all the requested networks.
            If the network_ids argument is None, return all the owner entries
            for ALL networks
        """
        owners = sharing.get_all_network_owners(network_ids,
                                                **ctx.in_header.__dict__)

        return [NetworkOwner(o) for o in owners]

    @rpc(SpyneArray(Integer),
         _returns=Unicode)
    def bulk_set_project_owners(ctx, project_owners, **kwargs):
        sharing.bulk_set_project_owners(project_owners,
                                       **ctx.in_header.__dict__)
        return 'OK'

    @rpc(SpyneArray(Integer),
         _returns=Unicode)
    def bulk_set_network_owners(ctx, network_owners, **kwargs):
        sharing.bulk_set_network_owners(network_owners,
                                        **ctx.in_header.__dict__)
        return 'OK'
