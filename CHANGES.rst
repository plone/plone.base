Changelog
=========

.. You should *NOT* be adding new change log entries to this file.
   You should create a file in the news directory instead.
   For helpful instructions, please see:
   https://github.com/plone/plone.releaser/blob/master/ADD-A-NEWS-ITEM.rst

.. towncrier release notes start

1.0.0b1 (2022-06-23)
--------------------

New features:


- Add Add image srcset's configuration including JSON schema definition to imaging-controlpanel [MrTango] (#5)
- Enable images in search results by default.
  [agitator] (#6)
- Add inline mode to tinymce config.
  [pbauer] (#7)
- Move ``Products.CMFPlone.utils._createObjectByType`` to here as ``utils.unrestricted_construct_instance``.
  [jensens] (#8)
- Add ``images`` interface with ``IImageScalesAdapter`` and ``IImageScalesFieldAdapter``.
  See https://github.com/plone/Products.CMFPlone/pull/3521
  [cekk, maurits] (#3521)
- ``ulocalized_time``: accept a string argument to long_format.
  For example: ``${a} ${d} hello guys ${b} ${Y}``.
  Taken over from `experimental.ulocalized_time <https://pypi.org/project/experimental.ulocalized_time/>`_.
  [maurits] (#3549)


Bug fixes:


- Support dollar signs in registry override for date formats.
  Then it uses the correct language in multilingual sites.
  [maurits] (#3550)


1.0.0a1 (2022-04-08)
--------------------

New features:


- Extend search controlpanel with options for results with images.
  [agitator] (#2)
- Initial structure and contents.
  [jensens] (#1)
