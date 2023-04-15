plone.base
==========

This package is the base package of the `CMS Plone <https://plone.org>`_.
It contains only interface contracts and basic features and utilities.
It was created to be able to maintain a clean dependency graph (`PLIP 3395 <https://github.com/plone/Products.CMFPlone/issues/3395>`_).

In details this package contains:

``interfaces`` (package)
    All ``zope.interface`` based contracts for the Plone core packages.
    In Plone 5 and below this was at ``Products.CMFPlone.interfaces``.

``i18nl10n`` (module)
    Plone specific internationalization and localization helpers.
    In Plone 5 and below this was at ``Products.CMFPlone.i18nl10n``.

``batch`` (module)
    Plone specific Batch based on ``plone.batching``.
    In Plone 5 and below this was at ``Products.CMFPlone.PloneBatch``.

``defaultpage`` (module)
    Plone specific handling of default pages with ``CMFDynamicViewFTI``.
    In Plone 5 and below this was at ``Products.CMFPlone.defaultpage``.

``permissions`` (module)
    CMFCore permissions declared public.
    In Plone 5 and below this was at ``Products.CMFPlone.permissions``.

``utils`` (module)
    A subset of commonly used and low-dependency utilities.
    In Plone 5 and below those been at ``Products.CMFPlone.utils`` (but not all were moved).

``navigationroot`` (module)
    Plone specific handling of navigation roots.
    Before those been at ``plone.app.layout.navigation.root``.

``__init__``
    ``PloneMessageFactory`` with ``plone`` i18n-domain and ``PloneLocalesMessageFactory`` with ``plonelocales`` domain.
    In Plone 5 and below this was at ``Products.CMFPlone.__init__``.

Source Code
===========

Contributors please read the document `Process for Plone core's development <https://docs.plone.org/develop/coredev/docs/index.html>`_

Sources are at the `Plone code repository hosted at Github <https://github.com/plone/plone.base>`_.

File issues at the `Products.CMFPlone issue tracker hosted at Github <https://github.com/plone/Products.CMFPlone/issues>`_.
