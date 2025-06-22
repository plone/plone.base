IClassicUISchema: Add new control panel.

Add new ``IClassicUISchema`` control panel schema with its ``plone.use_ajax_main_template`` setting.

When ``plone.use_ajax_main_template`` is enabled, and if we are in an XHR
request, Plone uses the AJAX main template. Note: This setting does not affect
the ``ajax_load`` query string parameter, which if set and evaluates to
``true``, will always trigger the AJAX main template.
