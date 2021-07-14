from django.contrib import admin
from .models import *


# Custom Admin class that will allow you to mark fields to be readonly on edits.
class CustomAdmin(admin.ModelAdmin):
    readonly_edit = tuple()

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Make team and owner readonly ONLY when the object already exists
            return self.readonly_fields + self.readonly_edit
        return self.readonly_fields


@admin.register(Event)
class EventAdmin(CustomAdmin):
    readonly_fields = ("object", "id")
    readonly_edit = ("team",)

    fields = ("id", "team", "event_type", "description", "user")


@admin.register(Member)
class MemberAdmin(CustomAdmin):
    readonly_fields = ("created", "id")
    readonly_edit = ("team", "owner")

    fields = (
        "id",
        "team",
        "owner",
        "role",
        "pronouns",
        "bio",
        "created",
        "activated",
        "deactivated",
    )


@admin.register(Tag)
class TagAdmin(CustomAdmin):
    readonly_fields = ("team_title_hash", "id", "created")

    fields = (
        "id",
        "team",
        "title",
        "created",
        "activated",
        "deactivated",
        "team_title_hash",
    )


@admin.register(Team)
class TeamAdmin(CustomAdmin):
    readonly_fields = ("created", "ticket_head", "id")

    fields = (("id", "ticket_head"), "name", "created", "activated", "deactivated")


@admin.register(TicketComment)
class TicketCommentAdmin(CustomAdmin):
    readonly_fields = ("created", "id")
    readonly_edit = ("ticket", "team")

    fields = (
        "id",
        "team",
        "ticket",
        "owner",
        "content",
        "created",
        "activated",
        "deactivated",
    )


@admin.register(TicketNode)
class TicketNodeAdmin(CustomAdmin):
    readonly_fields = ("id",)


@admin.register(TicketStatus)
class TicketStatusAdmin(CustomAdmin):
    readonly_fields = ("created", "id")
    readonly_edit = ("team",)

    fields = ("id", "team", "title", "color", "created", "activated", "deactivated")


@admin.register(TicketTag)
class TicketTagAdmin(CustomAdmin):
    readonly_fields = ("created", "id")
    readonly_edit = ("team",)

    fields = ("id", "team", "tag", "ticket", "created", "activated", "deactivated")


@admin.register(Ticket)
class TicketAdmin(CustomAdmin):
    readonly_fields = ("created", "ticket_number", "id", "activated")
    readonly_edit = ("team",)

    fields = (
        "id",
        "ticket_number",
        "team",
        "assigned_user",
        "due_date",
        "status",
        "title",
        "description",
        "created",
        "activated",
        "deactivated",
    )


@admin.register(PinnedTicket)
class PinnedTicketAdmin(CustomAdmin):
    readonly_fields = ("id", "pinned")
    readonly_edit = ("member", "ticket", "team")

    fields = ("id", "member", "ticket", "pinned", "team")


@admin.register(TeamInvite)
class TeamInviteAdmin(CustomAdmin):
    readonly_fields = ("id",)
    readonly_edit = ("team", "user")

    fields = ("id", "team", "user")
