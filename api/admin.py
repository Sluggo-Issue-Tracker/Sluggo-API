from django.contrib import admin
from .models import Profile, Snippet, Ticket


class TicketAdmin(admin.ModelAdmin):
    readonly_fields = ("created",)


# Register your models here.
admin.site.register(Profile)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(Snippet)
