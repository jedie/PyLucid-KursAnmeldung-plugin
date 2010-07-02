# coding:utf-8


from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from dbpreferences.forms import DBPreferencesBaseForm

from pylucid_project.apps.pylucid.shortcuts import failsafe_message


try:
    forms.EmailField().clean(settings.DEFAULT_FROM_EMAIL)
except forms.ValidationError, err:
    msg = (
        "Please change 'DEFAULT_FROM_EMAIL' in your settings.py,"
        " current value is: %s (Org.Error: %s)"
    ) % (settings.DEFAULT_FROM_EMAIL, err)
    failsafe_message(msg)


class KursAnmeldungPrefForm(DBPreferencesBaseForm):
    notify = forms.CharField(
        initial="\n".join(
            [i["email"] \
            for i in User.objects.filter(is_superuser=True).values("email")]
        ),
        required=False,
        help_text=_(
            "Notify these email addresses if a new comment submited"
            " (seperated by newline!)"
        ),
        widget=forms.Textarea(attrs={'rows': '5'}),
    )
    from_email = forms.EmailField(
        initial=settings.DEFAULT_FROM_EMAIL,
        help_text=_("from witch email address should be send mails"),
    )
    email_subject = forms.CharField(
        initial=settings.EMAIL_SUBJECT_PREFIX + "Anmeldung",
        help_text=_("verify email subject")
    )
    title = forms.CharField(
        initial="Anmeldung",
        help_text=_("Witch link title should be used?")
    )
    disable_text = forms.CharField(
        initial="<p>Kursanmeldung ist deaktiviert, versuche es später wieder.</p>",
        help_text=_("HTML code witch used as response, if course registration is disabled."),
        widget=forms.Textarea(),
    )
    active = forms.BooleanField(required=False,
        initial=True,
        help_text=_("Is the registration active or disabled?")
    )

    class Meta:
        app_label = 'kurs_anmeldung'
