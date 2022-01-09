from unittest import TestSuite

import doctest


def test_suite():
    suites = (
        doctest.DocFileSuite(
            "messages.rst",
            package="plone.base.tests",
        ),
    )
    return TestSuite(suites)
