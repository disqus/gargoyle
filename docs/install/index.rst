Installation
============

Install using pip::

	pip install -U gargoyle

Or alternatively, easy_install::

	easy_install -U gargoyle

Enable Gargoyle
---------------

Once you've downloaded the Gargoyle package, you simply need to add it to your ``INSTALLED_APPS``::

	INSTALLED_APPS = (
	    ...
	    'gargoyle',
	)

*If you do not use Nexus*, you will also need to enable discovery of ``gargoyle.py`` modules (which contain ConditionSets).
The best place to do this is within your ``urls.py`` file.

	>>> import gargoyle
	>>> gargoyle.autodiscover()

Nexus Frontend
--------------

While Gargoyle can be used without a frontend, we highly recommend using `Nexus <https://github.com/dcramer/nexus>`_.

Nexus will automatically detect Gargoyle's NexusModule, assuming you're using autodiscovery. If not, you will need to register
the module by hand:

	>>> from gargoyle.nexus_modules import GargoyleModule
	>>> nexus.site.register(GargoyleModule, 'gargoyle')

(Nexus is a replacement for your Django admin frontend, that works with django.contrib.admin)
