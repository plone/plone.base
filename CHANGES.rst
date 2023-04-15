Changelog
=========

.. You should *NOT* be adding new change log entries to this file.
   You should create a file in the news directory instead.
   For helpful instructions, please see:
   https://github.com/plone/plone.releaser/blob/master/ADD-A-NEWS-ITEM.rst

.. towncrier release notes start

1.1.1 (2023-04-15)
------------------

Internal:


- Update configuration files.
  [plone devs] (3333c742)


1.1.0 (2023-03-13)
------------------

New features:


- Move `plone.app.layout.navigation.root.getNavigationRoot` to `.navigationroot.get_navigation_root`.
  Move `plone.app.layout.navigation.root.getNavigationRootObject` to `.navigationroot.get_navigation_root_object`.
  Both are essential basic functions in Plone and not layout related at all.
  [jensens] (navigationroot)


Bug fixes:


- Move interface plone.app.layout.navigation.interfaces.INavigationRoot to plone.base.interfaces.siteroot and add a deprecated import to plone.app.layout.
  [jensens, gforcarda] (Plone-3731)


Internal:


- Update configuration files.
  [plone devs] (13d8d6c0)


1.0.3 (2023-02-08)
------------------

Bug fixes:


- Add `modal` property to `IActionSchema`.
  [petschki] (#27)


1.0.2 (2023-01-26)
------------------

Bug fixes:


- Add ``required=False`` to missing boolean field from syndication config.
  [frapell] (#14)
- Add missing TinyMCE plugin ``autolink`` to selectable plugins.
  [petschki] (#25)


1.0.1 (2022-12-10)
------------------

Bug fixes:


- Fix title and description for types_not_searched in ISearchSchema [danalvrz] (#24)


1.0.0 (2022-12-02)
------------------

Bug fixes:


- Final release for Plone 6.0.0. (#600)


1.0.0b5 (2022-10-04)
--------------------

New features:


- disable TinyMCE advlist plugin, it produces unclean inline styles [MrTango] (#21)
- Add inserttable to tinymce toolbar [MrTango] (#22)
- Add more tinyMCE table styles [MrTango] (#23)


1.0.0b4 (2022-10-02)
--------------------

Bug fixes:


- Fix content_css control-panel description.  [MrTango] (#17)
- Fix ``@@qsOptions`` view (essentially, listing of ``folder_contents``) when VHM roots the site on a ``plone.app.multilingual`` language folder as noted in `issue 159 <https://github.com/plone/plone.app.content/issues/159>`_.
  [Rudd-O] (#18)
- Fix ``get_top_site_from_url()`` when the path contains nonexistent objects (e.g. when creating a new Dexterity type or adding a new content instance). [Rudd-O] (#20)


1.0.0b3 (2022-08-31)
--------------------

Bug fixes:


- Fix returning of item_id if given in `pretty_title_or_id`.
  Remove unused code and outdated comment.
  [jensens] (#16)


1.0.0b2 (2022-07-21)
--------------------

Bug fixes:


- Fix Boolean Fields in ISiteSyndicationSettings, IFeedSettings, selection of true/false now possible
  [1letter] (#14)


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
