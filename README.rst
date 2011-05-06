Gargoyle
--------

Gargoyle is a platform built on top of Django which allows you to switch functionality of your application on and off based on conditions.

Screenshot
=========

.. image:: http://dl.dropbox.com/u/116385/Screenshots/-egenorlfjki.png

Installation
============

Install it with pip (or easy_install)::

	pip install gargoyle

Config
======

If you dont have `Nexus <https://github.com/dcramer/nexus>`_ already enabled, you will need to do that first.

(Nexus is a replacement for your Django admin frontend, that works with django.contrib.admin)

Now you just need to add Gargoyle to your ``INSTALLED_APPS``::

	INSTALLED_APPS = (
	    ...
	    'gargoyle',
	)

Usage
=====

Gargoyle is typically used in two fashions. The first and simplest, is as a decorator. The decorator will automatically integrate with filters registered to the ``User`` model, as well as IP address::

	from gargoyle.decorators import switch_is_active
	
	@switch_is_active('my switch name')
	def my_view(request):
	    return 'foo'

The second use is with the ``is_active`` method. This allows you to perform validation on your own custom objects::

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

Condition Sets
==============

Gargoyle provides an easy way to hook in your own condition sets to allow additional filters. Simply place a ConditionSet class in ``myapp/gargoyle.py`` and it will automatically discover it::

	from __future__ import absolute_import
	from gargoyle import gargoyle, conditions
	from django.contrib.sites.models import Site
	
	class SiteConditionSet(conditions.ModelConditionSet):
	    percent = conditions.Percent()
	    domain = conditions.String()
	
	gargoyle.register(SiteConditionSet(Site))

And now you can pass it into is_active::

	gargoyle.is_active('my switch name', Site.objects.get_current())