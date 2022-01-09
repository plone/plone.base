plone.base
==========

This package is the base package of the `CMS Plone <https://plone.org>`.
It contains only interface contracts and basic features and utilities.
It was created to be able to maintain a clean dependency graph.

In details this package contains:

``interfaces`` (package)
    All ``zope.interface`` based contracts for the Plone core packages.
    In Plone 5 and below this was at ``Products.CMFPlone.interfaces``.

``batch``
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


Source Code
===========

Contributors please read the document `Process for Plone core's development <https://docs.plone.org/develop/coredev/docs/index.html>`_

Sources are at the `Plone code repository hosted at Github <https://github.com/plone/plone.base>`_.

File issues at the `Products.CMFPlone issue tracker hosted at Github <https://github.com/plone/Products.CMFPlone/issues>`_.
