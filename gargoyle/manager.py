from django.conf import settings
from django.core.cache import get_cache
from django.http import HttpRequest

from gargoyle.models import Switch, DISABLED, SELECTIVE, GLOBAL, INHERIT, \
    INCLUDE, EXCLUDE
from gargoyle.proxy import SwitchProxy

from modeldict import ModelDict


class SwitchManager(ModelDict):
    DISABLED = DISABLED
    SELECTIVE = SELECTIVE
    GLOBAL = GLOBAL
    INHERIT = INHERIT

    INCLUDE = INCLUDE
    EXCLUDE = EXCLUDE

    def __init__(self, *args, **kwargs):
        self._registry = {}
        super(SwitchManager, self).__init__(*args, **kwargs)

    def __repr__(self):
        return "<%s: %s (%s)>" % (self.__class__.__name__, self.model, self._registry.values())

    def __getitem__(self, key):
        """
        Returns a SwitchProxy, rather than a Switch. It allows us to
        easily extend the Switches method and automatically include our
        manager instance.
        """
        return SwitchProxy(self, super(SwitchManager, self).__getitem__(key))

    def is_active(self, key, *instances, **kwargs):
        """
        Returns ``True`` if any of ``instances`` match an active switch. Otherwise
        returns ``False``.

        >>> gargoyle.is_active('my_feature', request) #doctest: +SKIP
        """
        default = kwargs.pop('default', False)

        # Check all parents for a disabled state
        parts = key.split(':')
        if len(parts) > 1:
            child_kwargs = kwargs.copy()
            child_kwargs['default'] = None
            result = self.is_active(':'.join(parts[:-1]), *instances, **child_kwargs)

            if result is False:
                return result
            elif result is True:
                default = result

        try:
            switch = self[key]
        except KeyError:
            # switch is not defined, defer to parent
            return default

        if switch.status == GLOBAL:
            return True
        elif switch.status == DISABLED:
            return False
        elif switch.status == INHERIT:
            return default

        conditions = switch.value
        # If no conditions are set, we inherit from parents
        if not conditions:
            return default

        if instances:
            # HACK: support request.user by swapping in User instance
            instances = list(instances)
            for v in instances:
                if isinstance(v, HttpRequest) and hasattr(v, 'user'):
                    instances.append(v.user)

        # check each switch to see if it can execute
        return_value = False

        for switch in self._registry.itervalues():
            result = switch.has_active_condition(conditions, instances)
            if result is False:
                return False
            elif result is True:
                return_value = True

        # there were no matching conditions, so it must not be enabled
        return return_value

    def register(self, condition_set):
        """
        Registers a condition set with the manager.

        >>> condition_set = MyConditionSet() #doctest: +SKIP
        >>> gargoyle.register(condition_set) #doctest: +SKIP
        """

        if callable(condition_set):
            condition_set = condition_set()
        self._registry[condition_set.get_id()] = condition_set

    def unregister(self, condition_set):
        """
        Unregisters a condition set with the manager.

        >>> gargoyle.unregister(condition_set) #doctest: +SKIP
        """
        if callable(condition_set):
            condition_set = condition_set()
        self._registry.pop(condition_set.get_id(), None)

    def get_condition_set_by_id(self, switch_id):
        """
        Given the identifier of a condition set (described in
        ConditionSet.get_id()), returns the registered instance.
        """
        return self._registry[switch_id]

    def get_condition_sets(self):
        """
        Returns a generator yielding all currently registered
        ConditionSet instances.
        """
        return self._registry.itervalues()

    def get_all_conditions(self):
        """
        Returns a generator which yields groups of lists of conditions.

        >>> for set_id, label, field in gargoyle.get_all_conditions(): #doctest: +SKIP
        >>>     print "%(label)s: %(field)s" % (label, field.label) #doctest: +SKIP
        """
        for condition_set in sorted(self.get_condition_sets(), key=lambda x: x.get_group_label()):
            group = unicode(condition_set.get_group_label())
            for field in condition_set.fields.itervalues():
                yield condition_set.get_id(), group, field

    def as_request(self, user=None, ip_address=None):
        from gargoyle.helpers import MockRequest

        return MockRequest(user, ip_address)


if hasattr(settings, 'GARGOYLE_CACHE_NAME'):
    gargoyle = SwitchManager(Switch, key='key', value='value', instances=True,
                         auto_create=getattr(settings, 'GARGOYLE_AUTO_CREATE', True),
                         cache=get_cache(settings.GARGOYLE_CACHE_NAME))
else:
    gargoyle = SwitchManager(Switch, key='key', value='value', instances=True,
                         auto_create=getattr(settings, 'GARGOYLE_AUTO_CREATE', True))
