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

        # with patch_formatstring("%Y-%m-%d %H:%M"):
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
