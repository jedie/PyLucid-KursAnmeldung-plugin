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


# Used in model validation:
MIN_MATRIKEL_NR = 10000
MAX_MATRIKEL_NR = 1000000
MAX_SEMESTER = 30


# Don't send mails, display them only.
# MAIL_DEBUG = True
MAIL_DEBUG = False
