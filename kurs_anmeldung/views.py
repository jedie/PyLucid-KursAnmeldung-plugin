# coding:utf-8

"""
    Kurs Anmeldung
    ~~~~~~~~~~~~~~

    :copyleft: 2009-2011 by Jens Diemer
    :license: GNU GPL v3 or above, see LICENSE for more details
"""

import datetime

from django.conf import settings
from django.contrib import messages
from django.core.mail.message import EmailMessage
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from pylucid_project.apps.pylucid.decorators import render_to
from pylucid_project.apps.pylucid.models import LogEntry
from pylucid_project.utils import crypt

from kurs_anmeldung.models import Kurs, KursAnmeldung
from kurs_anmeldung.preference_forms import KursAnmeldungPrefForm
from kurs_anmeldung.forms import KursAnmeldungForm



def _get_context_pref():
    pref_form = KursAnmeldungPrefForm()
    preferences = pref_form.get_preferences()
    context = {"title": preferences["title"]}
    return context, preferences


def _is_active(request, preferences):
    """
    return True/False for "courses registration is disabled" response
    """
    if not preferences["active"]:
        messages.debug(request, "Disabled by DBpreferences.")
        return False

    active_courses = Kurs.objects.all().filter(active=True).count()
    if active_courses == 0:
        messages.debug(request, "No active courses found.")
        return False

    return True



@render_to("kurs_anmeldung/verified.html")
def verify_email(request, hash):
    """ check a email hash """
    context, preferences = _get_context_pref()

    if not crypt.validate_sha_value(hash):
        LogEntry.objects.log_action(app_label="kurs_anmeldung", action="error",
            message="Wrong hash value %r" % hash
        )
        context["error"] = u"Hash wert im Link ist ungültig!"
        return context

    try:
        entry = KursAnmeldung.objects.get(verify_hash=hash)
    except Exception, err:
        msg = "Link ist ungültig!"
        LogEntry.objects.log_action(app_label="kurs_anmeldung", action="error",
            message="Can't get KursAnmeldung entry from hash value: %r" % hash
        )
        if settings.DEBUG:
            msg += " (Original error was: %s)" % err
        context["error"] = msg
        return context

    if entry.verified == True:
        messages.info(request, u"Hinweis: Deine Anmeldung wurde bereits bestätigt.")

    entry.verified = True
    entry.log(request, "verified via email hash link")
    entry.save()

    context["entry"] = entry
    return context


def _send_verify_email(request, preferences, db_entry, rnd_hash, new_entry):
    """ Send a verify email """

    location = reverse("KursAnmeldung-verify_email", kwargs={"hash":rnd_hash})
    verify_link = request.build_absolute_uri(location)

    # FIXME: convert to users local time.
    now = datetime.datetime.utcnow()

    email_context = {
        "verify_link": verify_link,
        "db_entry": db_entry,
        "now": now,
    }

    # Render the internal page
    emailtext = render_to_string("kurs_anmeldung/verify_mailtext.txt", email_context)

    # Get the preferences from the database:
    raw_notify_list = preferences["notify"]
    notify_list = raw_notify_list.splitlines()
    notify_list = [i.strip() for i in notify_list if i]

    email_kwargs = {
        "from_email": preferences["from_email"],
        "subject": preferences["email_subject"],
        "body": emailtext,
        "to": [db_entry.email],
        "bcc": notify_list,
    }

    if settings.KURS_ANMELDUNG.MAIL_DEBUG == True:
        msg = u"MAIL_DEBUG is on: No Email was sended!"
        messages.debug(request, msg)
        db_entry.log(request, msg)
        db_entry.mail_sended = False

        messages.debug(request, "django.core.mail.EmailMessage kwargs:")
        messages.debug(request, repr(email_kwargs))

        messages.debug(request, "debug mail text:")
        messages.debug(request, mark_safe("<pre>%s</pre>" % emailtext))
        return

    # We can't use django.core.mail.send_mail, because all members
    # of the recipient list will see the others in the 'To' field.
    # But we would like to notify the admins via 'Bcc' field.

#    connection = SMTPConnection(fail_silently=False)
    email = EmailMessage(**email_kwargs)

    try:
        sended = email.send(fail_silently=False)
    except Exception, err:
        msg = "Error sending mail: %s" % err
        LogEntry.objects.log_action(app_label="kurs_anmeldung", action="error",
            message=msg
        )
        db_entry.log(request, msg)
        db_entry.mail_sended = False
        if settings.DEBUG or request.user.is_staff:
            db_entry.save()
            raise
    else:
        db_entry.mail_sended = sended
        db_entry.log(request, "mail sended: %s" % sended)


@render_to("kurs_anmeldung/register_done.html")
def register_done(request):
    context, preferences = _get_context_pref()
    return context


@render_to("kurs_anmeldung/register.html")
def register(request):
    """
    Display the register form.
    """
    context, preferences = _get_context_pref()

    is_active = _is_active(request, preferences)
    if not is_active:
        # Course registration is disabled by preferences
        # or there exist no active course 
        disable_text = preferences["disable_text"]
        return mark_safe(disable_text)

    if request.method == 'POST':
        form = KursAnmeldungForm(request.POST)
        #messages.debug(request, repr(request.POST))
        if form.is_valid():
            # Create, but don't save the new instance.
            new_entry = form.save(commit=False)

            rnd_hash = crypt.get_new_seed()
            new_entry.verify_hash = rnd_hash

            new_entry.log(request, "created")

            # Save the new instance.
            new_entry.save()

            # save many-to-many data
            form.save_m2m()

            _send_verify_email(request, preferences, new_entry, rnd_hash, new_entry)

            # Save new log entries
            new_entry.save()

            messages.success(request, message="data saved")

            new_location = reverse("KursAnmeldung-register_done")
            return HttpResponseRedirect(new_location)
    else:
        form = KursAnmeldungForm()

    context["form"] = form
    context["url"] = request.path
    return context


