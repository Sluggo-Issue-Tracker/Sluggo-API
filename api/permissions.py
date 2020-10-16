from rest_framework import permissions
from hashlib import md5
from .models import Member, Team

"""
these all need to be deprecated as they are reliant on the old profile 
"""


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        return obj.owner == request.user


class BaseMemberPermissions(permissions.BasePermission):
    # this will throw a member not found exception
    def retrieveMemberRecord(self, username, team_id):
        team_id = "{}".format(team_id)
        member_pk = md5(team_id.encode()).hexdigest() + md5(username.encode()).hexdigest()
        print(member_pk)
        return Member.objects.get(pk=member_pk)


class IsMemberUser(BaseMemberPermissions):
    def has_object_permission(self, request, view, obj):
        try:
            self.retrieveMemberRecord(request.user.username, obj.team.id)
            permit = True
        except Member.DoesNotExist:
            permit = False

        return permit


class IsAdminMemberOrReadOnly(BaseMemberPermissions):
    """
    Custom permission to allow admin of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.

        team_id = obj.id if isinstance(obj, Team) else obj.team.id

        if request.method not in permissions.SAFE_METHODS:
            try:
                # Write permissions are only allowed to the owner of the object, or admin.
                member_record = self.retrieveMemberRecord(request.user.username, team_id)
                permit = member_record.role == "AD"

            except Member.DoesNotExist:
                permit = False

        else:
            permit = True

        return permit
