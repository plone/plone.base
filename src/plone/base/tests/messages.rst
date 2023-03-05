Test for Messages
=================

  >>> from plone.base import PloneMessageFactory as _

Messages without translation service set up
-------------------------------------------

Very simple message:

  >>> _('hello')
  'hello'

The domain is predefinied through the factory:

  >>> _('hello').domain
  'plone'

You can also define a default text:

  >>> msg = _('id', default='This is the text.')
  >>> msg
  'id'

  >>> msg.default
  'This is the text.'

And at last there is the possibility of variable substitution:

  >>> project = 'Plone'
  >>> msg = _('id', default='Hello ${name}', mapping={'name' : project})

  >>> msg
  'id'

  >>> msg.default
  'Hello ${name}'

  >>> msg.mapping
  {'name': 'Plone'}

Messages with translation service set up
----------------------------------------

Now we fake a translation domain. Usually you will have translations stored in
a po file and automatically translated by PTS or the Z3 translation service.

  >>> from zope.i18n.simpletranslationdomain import SimpleTranslationDomain
  >>> from zope.i18n.interfaces import ITranslationDomain

  >>> messages = {
  ...     ('de', 'This is a message.'): 'Dieses ist eine Nachricht.',
  ...     ('de', 'mail-notification'): 'Sie haben ${number} neue E-Mails.'}
  >>> mails = SimpleTranslationDomain('plone', messages)

  >>> from zope.component import provideUtility
  >>> provideUtility(mails, ITranslationDomain, name='plone')

Define the simple message:

  >>> msg = _('This is a message.')
  >>> msg
  'This is a message.'

We are still using the plone domain:

  >>> msg.domain
  'plone'

Verify that the translation succeeds:

  >>> from zope.i18n import translate
  >>> translate(msg, target_language='de')
  'Dieses ist eine Nachricht.'

Now try a message with variable substitution:

  >>> num = 42
  >>> note = _('mail-notification', default='You have ${number} new mails.',
  ...          mapping={'number': num})

  >>> note
  'mail-notification'

  >>> note.default
  'You have ${number} new mails.'

Try simple interpolation:

  >>> translate(note, target_language='en')
  'You have 42 new mails.'

And now try the real translation:

  >>> translate(note, target_language='de')
  'Sie haben 42 neue E-Mails.'

Messages inside page templates / tal
------------------------------------

We need a simple tal engine for the tests. The DummyEngine automatically
upper-cases all text.

  >>> from zope.tal.dummyengine import DummyEngine
  >>> engine = DummyEngine()

We use the Messages defined earlier.

  >>> msg
  'This is a message.'

  >>> note
  'mail-notification'

Inform the engine of our variables.

  >>> engine.setLocal('msg', msg)
  >>> engine.setLocal('note', note)

We also need a HTMLParser and TALInterpreter and add a simple convenience function
to get the parsed and interpreted text.

  >>> from zope.tal.htmltalparser import HTMLTALParser
  >>> from zope.tal.talinterpreter import TALInterpreter
  >>> from io import StringIO

  >>> def compile(source):
  ...     parser = HTMLTALParser()
  ...     parser.parseString(source)
  ...     program, macros = parser.getCode()
  ...     result = StringIO()
  ...     interpreter = TALInterpreter(program, {}, engine, stream=result)
  ...     interpreter()
  ...     return result.getvalue()

  >>> text = compile('<span i18n:translate="" tal:content="msg"/>')
  >>> '<span>THIS IS A MESSAGE.</span>' in text
  True

  >>> text = compile('<span i18n:translate="" tal:content="note"/>')
  >>> '<span>MAIL-NOTIFICATION</span>' in text
  True
