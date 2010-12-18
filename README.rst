Gargoyle
--------

Install it::

	pip install gargoyle
	
Enable it::

	# settings.py
	INSTALLED_APPS = (
	    ...
	    'gargoyle',
	)

	# urls.py
	
	urlpatterns = patterns('',
	    ('^gargoyle/', include('gargoyle.urls')),
	)

Use it::

	# as a decorator
	from gargoyle.decorators import switch_is_active
	
	@switch_is_active('my switch name')
	def my_view(request):
	    return 'foo'

	# within your functions
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

Extend it::

	# myapp/gargoyle.py
	from gargoyle import conditions
	from django.contrib.sites.models import Site
	
	class SiteConditionSet(conditions.ModelConditionSet):
	    percent = conditions.Percent()
	    domain = conditions.String()
	
	gargoyle.register(SiteConditionSet(Site))
	
	gargoyle.is_active('my switch name', Site.objects.get_current())