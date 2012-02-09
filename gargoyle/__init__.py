"""
gargoyle
~~~~~~~~

:copyright: (c) 2010 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

__all__ = ('gargoyle', 'ConditionSet', 'autodiscover', 'VERSION')

try:
    VERSION = __import__('pkg_resources').get_distribution('gargoyle').version
except Exception, e:
    VERSION = 'unknown'
