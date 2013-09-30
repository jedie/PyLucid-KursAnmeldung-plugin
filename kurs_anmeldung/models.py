# coding: utf-8

import datetime

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.functional import lazy
from django.utils.translation import ugettext_lazy as _

from django_tools.models import UpdateInfoBaseModel


class Kurs(UpdateInfoBaseModel):
    """
    e.g.:
    3dsmax - SS 2009 - Vormittags (9-12 Uhr)
    3dsmax - SS 2009 - Nachmittags (13-16 Uhr)

    inherited attributes from UpdateInfoBaseModel:
        createtime     -> datetime of creation
        lastupdatetime -> datetime of the last change
        createby       -> ForeignKey to user who creaded this entry
        lastupdateby   -> ForeignKey to user who has edited this entry
    """
    name = models.CharField(
        verbose_name="Kurs", help_text="Der Kursname",
        max_length=255, unique=True,
    )
    active = models.BooleanField(
        help_text="Ist der Kurs aktiv buchbar?"
    )

    site = models.ForeignKey(Site)
    # on_site = CurrentSiteManager('site')
    objects = models.Manager()
    # default_manager = models.Manager()

    def __init__(self, *args, **kwargs):
        super(Kurs, self).__init__(*args, **kwargs)

        # default=settings.SITE_ID would be set at startup
        # This is not right if dynamic SITE_ID used
        sites_field = self._meta.get_field_by_name("site")[0]
        sites_field.default = settings.SITE_ID

    def __unicode__(self):
        return u"Kurs %s" % (self.name)

    class Meta:
        verbose_name_plural = "Kurse"
        ordering = ("-lastupdatetime",)



def get_warteliste_choices():
    """
    FIXME: Without cache we get many DB queries here :(
    """
    cache_key = "KursAnmeldung_Warteliste_choices"
    choices = cache.get(cache_key)
    if choices:
        return choices

    choices = Kurs.objects.filter(active=False).values_list("id", "name")
    choices = list(choices) # evaluate queryset
    choices.append(
        (
            "unbekannt",
            "Hatte mich schon einmal eingetragen, weiß aber nicht mehr wann."
        )
    )
    cache.set(cache_key, choices)
    return choices


class KursAnmeldung(UpdateInfoBaseModel):
    """
    TODO: Hinzufügen von "Kursbesucht" oder so...

    inherited attributes from UpdateInfoBaseModel:
        createtime     -> datetime of creation
        lastupdatetime -> datetime of the last change
        createby       -> ForeignKey to user who creaded this entry
        lastupdateby   -> ForeignKey to user who has edited this entry
    """
    vorname = models.CharField(verbose_name="Vorname", max_length=128)
    nachname = models.CharField(verbose_name="Nachname", max_length=128)
    email = models.EmailField(
        verbose_name="Email", help_text="Deine gültige EMail Adresse.",
        # unique = True,
    )

    kurs_wahl = models.ForeignKey(Kurs, verbose_name="Kurs Wahl", related_name='kurs_wahl')

    besucht = models.BooleanField(help_text="Dieser Kurs wurde besucht.")
    abgebrochen = models.BooleanField(help_text="Dieser Kurs wurde besucht aber abgebrochen.")
    abgeschlossen = models.BooleanField(help_text="Dieser Kurs wurde besucht und abgeschlossen.")

    semester = models.PositiveIntegerField(
        verbose_name="Semester", help_text="In welchem Semester bist du?",
    )
    matrikel_nr = models.PositiveIntegerField(
        verbose_name="Matrikel Nr.", help_text="Deine Matrikel Nummer",
        # unique = True,
    )

    laptop = models.BooleanField(
        help_text="Kannst du einen Laptop mitbringen?"
    )

    warteliste = models.CharField(
        help_text=(
            "Stehst du schon in der Warteliste?"
            " In welchem Semester hattest du dich schon angemeldet?"
        ),
        blank=True,
        max_length=128, choices=lazy(get_warteliste_choices, list)()
    )
    note = models.TextField(
        null=True, blank=True,
        verbose_name="Anmerkung",
        help_text="Wenn du noch Fragen hast."
    )

    verify_hash = models.CharField(max_length=128)
    verified = models.BooleanField(default=False)
    mail_sended = models.BooleanField()
    logging = models.TextField(help_text="For internal logging")

    def clean_fields(self, exclude):
        """
        http://docs.djangoproject.com/en/dev/ref/models/instances/#django.db.models.Model.clean
        """
        message_dict = {}

        if "semester" not in exclude and self.semester > settings.KURS_ANMELDUNG.MAX_SEMESTER:
            message_dict["semester"] = ('Semester Wert scheint falsch zu sein.',)

        if "matrikel_nr" not in exclude and (
            self.matrikel_nr < settings.KURS_ANMELDUNG.MIN_MATRIKEL_NR
            or self.matrikel_nr > settings.KURS_ANMELDUNG.MAX_MATRIKEL_NR):
            message_dict["matrikel_nr"] = ('Die Matrikel Nummer scheint falsch zu sein.',)

        if message_dict:
            raise ValidationError(message_dict)

    def log(self, request, txt):
        now = datetime.datetime.utcnow()
        time_string = now.strftime("%Y-%m-%d %H:%M:%S")
        ip = request.META.get("REMOTE_ADDR", "???")
        self.logging += "\n%s %s %s" % (time_string, ip, txt)

    def log_html(self):
        """ for admin.ModelAdmin list_display """
        return "<br />".join(self.logging.splitlines())
    log_html.short_description = _('logging')
    log_html.allow_tags = True

    def __unicode__(self):
        return u"KursAnmeldung von %s %s" % (self.vorname, self.nachname)

    class Meta:
        unique_together = ("vorname", "nachname", "email")
        verbose_name_plural = "Kurs Anmeldungen"
        ordering = ("-lastupdatetime",)
