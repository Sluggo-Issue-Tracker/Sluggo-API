from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS
from hashlib import md5
from .models import Member, Team
from .methods import hash_team_id


class BaseMemberPermissions(BasePermission):
    # this will throw a member not found exception

    @staticmethod
    def retrieveMemberRecord(username, obj):
        team = obj if isinstance(obj, Team) else obj.team
        member_pk = hash_team_id(team, username)
        return Member.objects.get(pk=member_pk)


# only permit this if the user is approved
class IsMemberUser(BaseMemberPermissions):
    def has_object_permission(self, request, view, obj):

        try:
            self.retrieveMemberRecord(request.user.username, obj)
            return True
        except Member.DoesNotExist:
            return False


class IsMemberUserOrCreate(IsMemberUser):
    def has_object_permission(self, request, view, obj):
        if request.method not in SAFE_METHODS and request.method != "POST":
            return super().has_object_permission(request, view, obj)
        else:
            return True


class IsAdminMemberOrReadOnly(BaseMemberPermissions):
    """
    Custom permission to allow admin of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method not in SAFE_METHODS:
            try:
                # Write permissions are only allowed to the owner of the object, or admin.

                member_record = self.retrieveMemberRecord(request.user.username, obj)
                return member_record.is_admin()

            except Member.DoesNotExist:
                return False
        else:
            return True


class IsAdminMember(BaseMemberPermissions):
    def has_object_permission(self, request, view, object):
        try:
            member_record = self.retrieveMemberRecord(request.user.username, object)
            return member_record.is_admin()
        except Member.DoesNotExist:
            return False


class IsOwnerOrReadOnly(BaseMemberPermissions):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.

        if request.method in SAFE_METHODS:
            return True

        # hack. add HasOwner interface
        if hasattr(obj, "owner"):
            return obj.owner == request.user
        else:
            return True
