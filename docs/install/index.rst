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

If you do use ``gargoyle.py`` files and the autodiscovery code, you'll need to ensure your imports are not relative::

  from __future__ import absolute_import

  from gargoyle.conditions import ConditionSet
  # ...

Nexus Frontend
--------------

While Gargoyle can be used without a frontend, we highly recommend using `Nexus <https://github.com/dcramer/nexus>`_.

Nexus will automatically detect Gargoyle's NexusModule, assuming you're using autodiscovery. If not, you will need to register
the module by hand:

	>>> from gargoyle.nexus_modules import GargoyleModule
	>>> nexus.site.register(GargoyleModule, 'gargoyle')

(Nexus is a replacement for your Django admin frontend, that works with django.contrib.admin)

Disabling Auto Creation
-----------------------

Under some conditions you may not want Gargoyle to automatically create switches that don't currently exist. To disable this behavior,
you may use the ``GARGOYLE_AUTO_CREATE`` setting your ``settings.py``::

    GARGOYLE_AUTO_CREATE = False

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

