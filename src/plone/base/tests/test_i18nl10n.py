""" Unit tests for plone.base.i18nl10n module. """

from contextlib import contextmanager
from unittest.mock import patch
from zope.publisher.browser import TestRequest

import datetime
import DateTime
import locale
import unittest


class DummyContext:
    """Dummy context with only a REQUEST.

    The ulocalized_time method needs a context, for example the Plone portal,
    but it is only used to get the request:

    request = aq_acquire(context, "REQUEST")
    """

    def __init__(self):
        self.REQUEST = TestRequest()


@contextmanager
def patch_formatstring(value=None):
    import plone.base.i18nl10n

    with patch.object(
        plone.base.i18nl10n, "get_formatstring_from_registry", return_value=value
    ):
        yield


# Mock translations
TRANSLATIONS = {
    "de": {
        "date_format_short": "DE: ${d}.${m}.${Y}",
    },
    "nl": {
        "date_format_short": "NL: ${a} ${d} ${b} ${Y}",
        "date_format_long": "NL: ${A} ${d} ${B} ${Y}",
        "weekday_sun": "zondag",
        "weekday_sun_abbr": "zo",
        "month_mar": "maart",
        "month_mar_abbr": "mrt",
    },
    None: {
        "date_format_short": "${b} ${d}, ${Y}",
        "date_format_long": "${b} ${d}, ${Y} ${I}:${M} ${p}",
        "time_format": "${I}:${M} ${p}",
        "weekday_sun": "Sunday",
        "weekday_sun_abbr": "Su",
        "month_mar": "March",
        "month_mar_abbr": "Mar",
    },
}


def mock_translate(msgid, *args, **kwargs):
    from zope.i18n import translate

    target_language = kwargs.get("target_language")
    default = kwargs.get("default")
    override = False
    # Note: we have translations for target_language=None .
    try:
        override = TRANSLATIONS[target_language][msgid]
    except Exception:
        pass
    # Even if the TRANSLATIONS lookup worked, we may still need to call the
    # original translate function.  This depends on the keyword arguments having
    # a mapping and/or a default.
    if override:
        msgid = override
    standard = translate(msgid, *args, **kwargs)
    if standard == default and override:
        # Example: original msgid is "weekday_sun", just like the default,
        # and this is the standard answer.  But override is "zondag".
        # The override should win then.
        return override
    return standard


@contextmanager
def patch_translate():
    import plone.base.i18nl10n

    with patch.object(plone.base.i18nl10n, "translate", wraps=mock_translate):
        yield


@contextmanager
def use_locale(value=None):
    orig = locale.getlocale(locale.LC_TIME)[0] or "C"
    try:
        worked = locale.setlocale(locale.LC_TIME, value)
    except locale.Error:
        worked = False
    yield worked
    locale.setlocale(locale.LC_TIME, orig)


class BasicI18nl10nTests(unittest.TestCase):
    def test_regexp_dt_format_string_regexp(self):
        from plone.base.i18nl10n import _dt_format_string_regexp

        dt_string = "%Y-%m-%d %H:%M"
        locales_string = "${H}:${M}"

        # test for strftime format string
        self.assertTrue(bool(_dt_format_string_regexp.findall(dt_string)))
        self.assertFalse(bool(_dt_format_string_regexp.findall(locales_string)))

    def test_regexp_interp_regex(self):
        from plone.base.i18nl10n import _interp_regex

        locales_string = "${H}:${M}"

        # test for locale string elements:
        self.assertEqual(
            _interp_regex.findall(locales_string),
            ["${H}", "${M}"],
        )

    def test_utranslate(self):
        from plone.base.i18nl10n import utranslate

        request = TestRequest()

        # Test string value
        value = utranslate("domain", "foo", context=request)
        self.assertEqual(value, "foo")

        # Test empty string
        value = utranslate("domain", "", context=request)
        self.assertEqual(value, "")

        # Test empty domain
        value = utranslate("", "foo", context=request)
        self.assertEqual(value, "foo")

        # Test default is None
        value = utranslate("domain", "foo", context=request, default=None)
        self.assertEqual(value, "foo")

        # Test default is other
        value = utranslate("domain", "foo", context=request, default="other")
        self.assertEqual(value, "other")

        # Test a target language.
        value = utranslate("domain", "foo", context=request, target_language="nl")
        self.assertEqual(value, "foo")

    def test_ulocalized_time_fallbacks(self):
        """Test the fallbacks in the ulocalized_time method.

        The ulocalized_time method uses one of three formats, based on the arguments:

        if time_only:
            msgid = "time_format"  # fallback: %H:%M
        elif long_format:
            msgid = "date_format_long"  # fallback: %Y-%m-%d %H:%M
        else:
            msgid = "date_format_short"  # fallback: %Y-%m-%d

        The ulocalized_time method looks this msgid up in a po file to see which format
        to use when calling 'strftime'.  In these unit tests, no translations are
        available, so the hardcoded fallbacks are used.

        Default Plone site has a few records with which you can override this.
        See get_formatstring_from_registry.  In plain unit tests this call fails,
        because no registry has been set up.

        Easiest way for us to test this, is then by mocking/patching this function.
        To test the fallbacks, we only have to use None as return value.
        """
        from plone.base.i18nl10n import ulocalized_time

        context = DummyContext()
        with patch_formatstring():
            # We test all combinations of long_format and time_only,
            # although not all make sense (both true).
            self.assertEqual(
                ulocalized_time(
                    "Mar 9, 1997 1:45pm",
                    long_format=True,
                    time_only=False,
                    context=context,
                ),
                "1997-03-09 13:45",
            )
            self.assertEqual(
                ulocalized_time(
                    "Mar 9, 1997 1:45pm",
                    long_format=False,
                    time_only=False,
                    context=context,
                ),
                "1997-03-09",
            )
            self.assertEqual(
                ulocalized_time(
                    "Mar 9, 1997 1:45pm",
                    long_format=False,
                    time_only=True,
                    context=context,
                ),
                "13:45",
            )
            self.assertEqual(
                ulocalized_time(
                    "Mar 9, 1997 1:45pm",
                    long_format=False,
                    time_only=True,
                    context=context,
                ),
                "13:45",
            )

    def test_ulocalized_time_formats(self):
        """Test different formats in the ulocalized_time method.

        See notes in ulocalized_time_fallbacks.  Best way to check non-default formats,
        is to patch get_formatstring_from_registry.  This results in ignoring the
        time_only and long_format options, so we do not pass them here.
        """
        from plone.base.i18nl10n import ulocalized_time

        context = DummyContext()
        with patch_formatstring("%H:%M %d-%m-%Y"):
            self.assertEqual(
                ulocalized_time(
                    "Mar 9, 1997 1:45pm",
                    context=context,
                ),
                "13:45 09-03-1997",
            )
        with patch_formatstring("German: %Y.%m.%d"):
            self.assertEqual(
                ulocalized_time(
                    "Mar 9, 1997 1:45pm",
                    context=context,
                ),
                "German: 1997.03.09",
            )
        # Use week days and month names.
        with patch_formatstring("%A %B %d %Y"):
            self.assertEqual(
                ulocalized_time(
                    "Mar 9, 1997 1:45pm",
                    context=context,
                ),
                "Sunday March 09 1997",
            )
        with patch_formatstring("%a %b %d %Y"):
            self.assertEqual(
                ulocalized_time(
                    "Mar 9, 1997 1:45pm",
                    context=context,
                ),
                "Sun Mar 09 1997",
            )

    def test_ulocalized_time_translate_no_language_format(self):
        """Test translations in the ulocalized_time method.

        This is mostly about translating week days and month names.
        But also about using a different format for a language.

        For this test, nothing was changed.
        A few other tests follow, where we did overrides.
        """
        from plone.base.i18nl10n import ulocalized_time

        context = DummyContext()
        with patch_formatstring():
            with patch_translate():
                # French gets the default.
                self.assertEqual(
                    ulocalized_time(
                        "Mar 9, 1997 1:45pm",
                        context=context,
                        target_language="fr",
                    ),
                    "1997-03-09",
                )

    def test_ulocalized_time_translate_language_format(self):
        from plone.base.i18nl10n import ulocalized_time

        context = DummyContext()
        with patch_formatstring():
            with patch_translate():
                # For German we have mocked a different date_format_short.
                self.assertEqual(
                    ulocalized_time(
                        "Mar 9, 1997 1:45pm",
                        context=context,
                        target_language="de",
                    ),
                    "DE: 09.03.1997",
                )

    def test_ulocalized_time_translate_weekdays_month_names_short(self):
        from plone.base.i18nl10n import ulocalized_time

        context = DummyContext()
        with patch_formatstring():
            with patch_translate():
                # For Dutch we have mocked a different date_format_short,
                # using abbreviations for week days and month names.
                self.assertEqual(
                    ulocalized_time(
                        "Mar 9, 1997 1:45pm",
                        context=context,
                        target_language="nl",
                    ),
                    "NL: zo 09 mrt 1997",
                )

    def test_ulocalized_time_translate_weekdays_month_names_long(self):
        from plone.base.i18nl10n import ulocalized_time

        context = DummyContext()
        with patch_formatstring():
            with patch_translate():
                # For Dutch we have mocked a different date_format_long,
                # using week days and month names.
                self.assertEqual(
                    ulocalized_time(
                        "Mar 9, 1997 1:45pm",
                        long_format=True,
                        context=context,
                        target_language="nl",
                    ),
                    "NL: zondag 09 maart 1997",
                )

    def test_ulocalized_time_dollar_classic_format_english(self):
        # When the format is a classic strftime format as you would use in standard
        # Python, the week days and month names are not translated.
        # Python will do translation using the current locale.
        # In these tests, it is useless to pass a target_language.

        from plone.base.i18nl10n import ulocalized_time

        context = DummyContext()
        with patch_formatstring("%A %B %d %Y"):
            # Default is English, which needs no translation.
            # Do not assume that English is the locale on the system though.
            with use_locale("C") as available:
                if not available:
                    self.skipTest("English (C) locale not available")
                self.assertEqual(
                    ulocalized_time(
                        "Mar 9, 1997 1:45pm",
                        context=context,
                    ),
                    "Sunday March 09 1997",
                )

    def test_ulocalized_time_dollar_classic_format_dutch(self):
        from plone.base.i18nl10n import ulocalized_time

        context = DummyContext()
        with patch_formatstring("%A %B %d %Y"):
            # But how about Dutch?  This can only be tested if we have the this locale
            # and set it here.
            with use_locale("nl_NL") as available:
                if not available:
                    self.skipTest("Dutch (nl_NL) locale not available")
                self.assertEqual(
                    ulocalized_time(
                        "Mar 9, 1997 1:45pm",
                        context=context,
                    ),
                    "zondag maart 09 1997",
                )

    def test_ulocalized_time_dollar_format_translates_weekdays_month_names_long(self):
        # When the format is taken from the registry instead of from po files,
        # the week days and month names should still be translated.
        from plone.base.i18nl10n import ulocalized_time

        context = DummyContext()
        with patch_formatstring("${A} ${B} ${d} ${Y}"):
            with patch_translate():
                # English should be no trouble, because it needs no translation.
                self.assertEqual(
                    ulocalized_time(
                        "Mar 9, 1997 1:45pm",
                        context=context,
                        # target_language="en",
                    ),
                    "Sunday March 09 1997",
                )
                # But how about Dutch?  In the tests we have Dutch translations for
                # Sunday and March, and they should be used.
                self.assertEqual(
                    ulocalized_time(
                        "Mar 9, 1997 1:45pm",
                        context=context,
                        target_language="nl",
                    ),
                    "zondag maart 09 1997",
                )

    def test_ulocalized_time_explicit_long_format_dollar(self):
        # We took over a change from experimental.ulocalized_time:
        # allow passing an explicit long_format.
        from plone.base.i18nl10n import ulocalized_time

        context = DummyContext()
        with patch_formatstring():
            with patch_translate():
                self.assertEqual(
                    ulocalized_time(
                        "Mar 9, 1997 1:45pm",
                        long_format="NL: ${A} go ${d} crazy ${B} ${Y}!",
                        context=context,
                        target_language="nl",
                    ),
                    "NL: zondag go 09 crazy maart 1997!",
                )

    def test_ulocalized_time_explicit_long_format_classic(self):
        from plone.base.i18nl10n import ulocalized_time

        context = DummyContext()
        with patch_formatstring():
            with patch_translate():
                # You should not use %, but it can work.
                with use_locale("nl_NL") as available:
                    if not available:
                        self.skipTest("Dutch (nl_NL) locale not available")
                    self.assertEqual(
                        ulocalized_time(
                            "Mar 9, 1997 1:45pm",
                            long_format="NL: %A go %d crazy %B %Y!",
                            context=context,
                            # this is ignored:
                            target_language="de",
                        ),
                        "NL: zondag go 09 crazy maart 1997!",
                    )

    def test_ulocalized_time_no_context(self):
        # Without context, we fall back to ISO8601.
        from plone.base.i18nl10n import ulocalized_time

        self.assertEqual(
            ulocalized_time("Mar 9, 1997 1:45pm", context=None), "1997-03-09T13:45:00"
        )

    def test_ulocalized_time_none(self):
        # Test passing None.
        from plone.base.i18nl10n import ulocalized_time

        context = DummyContext()

        with patch_formatstring():
            self.assertEqual(
                ulocalized_time(
                    "Mar 9, 1997 1:45pm",
                    time_only=None,
                    context=context,
                ),
                "1997-03-09",
            )
            self.assertEqual(
                ulocalized_time(
                    "Mar 9, 1997 1:45pm",
                    time_only=None,
                    domain=None,
                    context=context,
                ),
                "1997-03-09",
            )

    def test_ulocalized_time_fetch_error(self):
        from plone.base.i18nl10n import ulocalized_time

        # You should pass a DateTime, although the code does try to convert.
        # If this fails, get get None back.  Apparently in an old bug, an error
        # got passed like this:
        self.assertEqual(ulocalized_time("(Missing.Value,), {}"), None)
        self.assertEqual(ulocalized_time("Hello world"), None)
        self.assertEqual(ulocalized_time([]), None)

    def test_ulocalized_time_conversion(self):
        from plone.base.i18nl10n import ulocalized_time

        # You should pass a DateTime, but when the argument is accepted by DateTime,
        # conversion automatically happens.  When it depends on the time of day,
        # or on the time zone, we cannot compare the full result.
        now = DateTime.DateTime()
        day = now.strftime("%Y-%m-%d")
        self.assertTrue(ulocalized_time(None).startswith(day))
        self.assertTrue(ulocalized_time(datetime.datetime.now()).startswith(day))
        self.assertTrue(ulocalized_time(86400).startswith("1970-01"))
        self.assertEqual(ulocalized_time("Jan 27 1976"), "1976-01-27T00:00:00")
