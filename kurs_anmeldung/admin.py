# coding:utf-8

from django.contrib import admin
from django.conf import settings

from reversion.admin import VersionAdmin

from pylucid_project.apps.pylucid.decorators import render_to

from kurs_anmeldung.models import Kurs, KursAnmeldung
from django.shortcuts import render_to_response
from django.template.context import RequestContext


class KursAdmin(VersionAdmin):
    list_display = ("id", "name", "active", "site")
    list_display_links = ("name",)
    list_filter = ("active", "site")
    date_hierarchy = 'lastupdatetime'
    search_fields = ("name",)
    ordering = ('-lastupdatetime',)

admin.site.register(Kurs, KursAdmin)



class KursAnmeldungAdmin(VersionAdmin):
    @render_to()
    def get_emails_action(self, request, queryset):
        context = {"queryset":queryset}
        response = render_to_response("kurs_anmeldung/get_emails_action.html", context, context_instance=RequestContext(request))
        return response

    actions = ['get_emails_action']
    list_display = (
        "id",
        "vorname", "nachname", "kurs_wahl", "laptop", "warteliste",
        "email", "verified",
        "note", "log_html",
#        
#        "createby", "lastupdateby",
    )
    list_display_links = ("id", "email",)
    list_filter = (
        "verified", "kurs_wahl", "laptop", "kurs_wahl", "warteliste",
        "besucht", "abgebrochen", "abgeschlossen",
        "createby", "lastupdateby",
    )
    date_hierarchy = 'lastupdatetime'
    search_fields = ("vorname", "nachname", "email", "note", "logging")
    ordering = ('-lastupdatetime',)

admin.site.register(KursAnmeldung, KursAnmeldungAdmin)
