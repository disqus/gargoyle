Usage
=====

Gargoyle is designed to work around a very simple API. Generally, you pass in the switch key and a list of instances
to check this key against.

@switch_is_active
~~~~~~~~~~~~~~~~~

The simplest way to use Gargoyle is as a decorator. The decorator will automatically integrate with
filters registered to the ``User`` model, as well as IP address (using RequestConditionSet)::

	from gargoyle.decorators import switch_is_active
	
	@switch_is_active('my switch name')
	def my_view(request):
	    return 'foo'

In the case of the switch being inactive and you are using the decorator, a 404 error is raised. You may also redirect
the user to an absolute URL (relative to domain), or a named URL pattern::

	# if redirect_to starts with a /, we assume it's a url path
	@switch_is_active('my switch name', redirect_to='/my/url/path)

	# alternatively use the url mapper
	@switch_is_active('my switch name', redirect_to='access_denied')

gargoyle.is_active
~~~~~~~~~~~~~~~~~~

An alternative, more flexible use of Gargoyle is with the ``is_active`` method. This allows you
to perform validation on your own custom objects::

	from gargoyle import gargoyle
	
	def my_function(request):
	    if gargoyle.is_active('my switch name', request):
	        return 'foo'
	    else:
	        return 'bar'

	# with custom objects
	from gargoyle import gargoyle
	
	def my_method(user):
	    if gargoyle.is_active('my switch name', user):
	        return 'foo'
	    else:
	        return 'bar'

ifswitch
~~~~~~~~

If you prefer to use templatetags, Gargoyle provides a helper called ``ifswitch`` to give you easy conditional blocks based on active switches (for the request)::

	{% load gargoyle_tags %}
	
	{% ifswitch switch_name %}
	    switch_name is active!
	{% else %}
	    switch_name is not active :(
	{% endifswitch %}

``ifswitch`` can also be used with custom objects, like the ``gargoyle.is_active`` method::

	{% ifswitch "my switch name" user %}
	    "my switch name" is active!
	{% endifswitch %}

Default Switch States
~~~~~~~~~~~~~~~~~~~~~

The GARGOYLE_SWITCH_DEFAULTS setting allows engineers to set the default state of a switch before it's been added via the gargoyle admin interface. In your settings.py add something like::

    GARGOYLE_SWITCH_DEFAULTS = {
        'new_switch': {
          'is_active': True,
          'label': 'New Switch',
          'description': 'When you want the newness',
        },
        'funky_switch': {
          'is_active': False,
          'label': 'Funky Switch',
          'description': 'Controls the funkiness.',
        },
    }

