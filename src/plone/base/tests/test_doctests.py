from unittest import TestSuite

import doctest
import unittest.suite


def test_suite() -> unittest.suite.TestSuite:
    suites = (
        doctest.DocFileSuite(
            "messages.rst",
            package="plone.base.tests",
        ),
    )
    return TestSuite(suites)
