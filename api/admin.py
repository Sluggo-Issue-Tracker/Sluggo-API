from django.contrib import admin
from .models import (Ticket, Member, Team, TicketComment, TicketStatus,
                     TicketNode, TicketTag, Event)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    readonly_fields = ("created", )


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    readonly_fields = ("created", )

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Make team and owner readonly ONLY when the object already exists
            return self.readonly_fields + ("team", "owner")
        return self.readonly_fields

    fields = ("team", "owner", "role", "pronouns", "bio")


# Register your models here.
admin.site.register(Team)
admin.site.register(TicketComment)
admin.site.register(TicketStatus)
admin.site.register(TicketNode)
admin.site.register(TicketTag)
admin.site.register(Event)
