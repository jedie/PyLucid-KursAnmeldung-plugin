# coding: utf-8

"""
    kurs_anmeldung settings
    ~~~~~~~~~~~~~~~~~~~~~~~

    All own settings for the 'kurs_anmeldung' app.

    usage, put this into your local_settings.py:
    ----------------------------------------------------------------------------
    # import the 'Foo' app settings
    from kurs_anmeldung import kurs_anmeldung_settings as KURS_ANMELDUNG

    # example overwrite settings:
    KURS_ANMELDUNG.FOO = 20
    KURS_ANMELDUNG.BAR = True
    ----------------------------------------------------------------------------
"""


WARTELISTE = (
    ("-", "Habe mich vorher noch nicht für diesen Kurs eingeschrieben."),
    ("SS08", "SS 2008"),
    ("WS08/09", "WS 2008/2009"),
    ("SS09", "SS 2009"),
    ("WS09/10", "WS 2009/2010"),
    ("SS10", "SS 2010"),
    ("WS10/11", "WS 2010/2011"),
    ("SS11", "SS 2011"),
    (
        "unbekannt",
        "Hatte mich schon einmal eingetragen, weiß aber nicht mehr wann."
    ),
)

# Used in model validation:
MIN_MATRIKEL_NR = 10000
MAX_MATRIKEL_NR = 1000000
MAX_SEMESTER = 30


# Don't send mails, display them only.
# MAIL_DEBUG = True
MAIL_DEBUG = False
