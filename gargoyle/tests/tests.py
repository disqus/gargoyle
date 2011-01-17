from django.contrib.auth.models import User, AnonymousUser
from django.core.cache import cache
from django.http import HttpRequest, Http404
from django.test import TestCase

from gargoyle.models import Switch, SELECTIVE, DISABLED, GLOBAL
from gargoyle.decorators import switch_is_active
from gargoyle import autodiscover, gargoyle

autodiscover()

class GargoyleTest(TestCase):
    urls = 'gargoyle.tests.urls'
    
    def setUp(self):
        self.user = User.objects.create(username='foo', email='foo@example.com')

    def test_builtin_discovery(self):
        self.assertTrue('gargoyle.builtins.IPAddressConditionSet' in gargoyle._registry)
        self.assertTrue('gargoyle.builtins.UserConditionSet(auth.user)' in gargoyle._registry)

    def test_user(self):
        condition_set = 'gargoyle.builtins.UserConditionSet(auth.user)'
        
        # we need a better API for this (model dict isnt cutting it)
        switch = Switch.objects.create(
            key='test',
            status=SELECTIVE,
        )
        switch = gargoyle['test']
        
        switch.add_condition(
            condition_set=condition_set,
            field_name='percent',
            condition='0-50',
        )

        user = User(pk=5)
        self.assertTrue(gargoyle.is_active('test', user))

        user = User(pk=8771)
        self.assertFalse(gargoyle.is_active('test', user))
        
        switch.add_condition(
            condition_set=condition_set,
            field_name='is_staff',
            condition='1',
        )

        user = User(pk=8771, is_staff=True)
        self.assertTrue(gargoyle.is_active('test', user))

        user = User(pk=8771, is_superuser=True)
        self.assertFalse(gargoyle.is_active('test', user))

        switch.add_condition(
            condition_set=condition_set,
            field_name='is_superuser',
            condition='1',
        )
        
        user = User(pk=8771, is_superuser=True)
        self.assertTrue(gargoyle.is_active('test', user))

    def test_exclusions(self):
        condition_set = 'gargoyle.builtins.UserConditionSet(auth.user)'
        
        switch = Switch.objects.create(
            key='test',
            status=SELECTIVE,
        )
        switch = gargoyle['test']
        
        switch.add_condition(
            condition_set=condition_set,
            field_name='percent',
            condition='0-50',
            exclude=True,
        )
        switch.add_condition(
            condition_set=condition_set,
            field_name='username',
            condition='foo',
        )
        
        user = User(pk=5, username='foo')
        self.assertFalse(gargoyle.is_active('test', user))

        user = User(pk=8771, username='foo')
        self.assertTrue(gargoyle.is_active('test', user))

    def test_decorator_for_user(self):
        condition_set = 'gargoyle.builtins.UserConditionSet(auth.user)'
        
        switch = Switch.objects.create(
            key='test',
            status=DISABLED,
        )
        switch = gargoyle['test']
        
        @switch_is_active('test')
        def test(request):
            return True

        request = HttpRequest()
        request.user = self.user

        self.assertRaises(Http404, test, request)

        switch.status = SELECTIVE
        switch.save()

        self.assertTrue(test(request))

        switch.add_condition(
            condition_set=condition_set,
            field_name='username',
            condition='foo',
        )
        
        self.assertTrue(test(request))

    def test_decorator_for_ip_address(self):
        condition_set = 'gargoyle.builtins.IPAddressConditionSet'
        
        switch = Switch.objects.create(
            key='test',
            status=DISABLED,
        )
        switch = gargoyle['test']
        
        @switch_is_active('test')
        def test(request):
            return True

        request = HttpRequest()
        request.META['REMOTE_ADDR'] = '192.168.1.1'

        self.assertRaises(Http404, test, request)

        switch.status = SELECTIVE
        switch.save()

        switch.add_condition(
            condition_set=condition_set,
            field_name='ip_address',
            condition='192.168.1.1',
        )

        self.assertTrue(test(request))

        switch.remove_condition(
            condition_set=condition_set,
            field_name='ip_address',
            condition='192.168.1.1',
        )

        self.assertRaises(Http404, test, request)

        switch.add_condition(
            condition_set=condition_set,
            field_name='ip_address',
            condition='192.168.1.1',
        )

        self.assertTrue(test(request))

        switch.clear_conditions(
            condition_set=condition_set,
            field_name='ip_address',
        )

        switch.add_condition(
            condition_set=condition_set,
            field_name='percent',
            condition='50-100',
        )

        self.assertTrue(test(request))

        switch.clear_conditions(
            condition_set=condition_set,
        )

        switch.add_condition(
            condition_set=condition_set,
            field_name='percent',
            condition='0-50',
        )

        self.assertRaises(Http404, test, request)

    def test_global(self):
        condition_set = 'gargoyle.builtins.UserConditionSet(auth.user)'
        
        switch = Switch.objects.create(
            key='test',
            status=SELECTIVE,
        )
        switch = gargoyle['test']

        self.assertTrue(gargoyle.is_active('test'))
        self.assertTrue(gargoyle.is_active('test', self.user))
        
        switch.status = GLOBAL
        switch.save()

        self.assertTrue(gargoyle.is_active('test'))
        self.assertTrue(gargoyle.is_active('test', self.user))

    def test_disable(self):
        switch = Switch.objects.create(key='test')
        
        switch = gargoyle['test']
        
        switch.status = DISABLED
        switch.save()

        self.assertFalse(gargoyle.is_active('test'))

        self.assertFalse(gargoyle.is_active('test', self.user))

    def test_expiration(self):
        switch = Switch.objects.create(key='test')
        
        switch = gargoyle['test']
        
        switch.status = DISABLED
        switch.save()

        self.assertFalse(gargoyle.is_active('test'))

        Switch.objects.filter(key='test').update(value={}, status=SELECTIVE)

        # cache shouldn't have expired
        self.assertFalse(gargoyle.is_active('test'))

        # in memory cache shouldnt have expired
        cache.delete(gargoyle.cache_key)
        self.assertFalse(gargoyle.is_active('test'))
        switch.status, switch.value = SELECTIVE, {}
        # Ensure post save gets sent
        gargoyle._post_save(sender=None, instance=switch, created=False)

        # any request should expire the in memory cache
        self.client.get('/')
        
        self.assertTrue(gargoyle.is_active('test'))

    def test_anonymous_user(self):
        condition_set = 'gargoyle.builtins.UserConditionSet(auth.user)'

        switch = Switch.objects.create(key='test')
        
        switch = gargoyle['test']
        
        switch.status = SELECTIVE
        switch.save()
        
        user = AnonymousUser()

        self.assertTrue(gargoyle.is_active('test', user))

        switch.add_condition(
            condition_set=condition_set,
            field_name='percent',
            condition='1-10',
        )

        self.assertFalse(gargoyle.is_active('test', user))

        switch.clear_conditions(condition_set=condition_set)

        self.assertTrue(gargoyle.is_active('test', user))

        switch.add_condition(
            condition_set=condition_set,
            field_name='is_anonymous',
            condition='1',
        )

        self.assertTrue(gargoyle.is_active('test', user))

        switch.add_condition(
            condition_set=condition_set,
            field_name='percent',
            condition='1-10',
        )

        self.assertTrue(gargoyle.is_active('test', user))

    def test_ip_address(self):
        condition_set = 'gargoyle.builtins.IPAddressConditionSet'
        
        switch = Switch.objects.create(
            key='test',
            status=SELECTIVE,
        )
        switch = gargoyle['test']


        request = HttpRequest()
        request.META['REMOTE_ADDR'] = '192.168.1.1'

        self.assertTrue(gargoyle.is_active('test', request))

        switch.add_condition(
            condition_set=condition_set,
            field_name='ip_address',
            condition='192.168.1.1',
        )

        self.assertTrue(gargoyle.is_active('test', request))

        switch.clear_conditions(condition_set=condition_set)
        switch.add_condition(
            condition_set=condition_set,
            field_name='ip_address',
            condition='127.0.0.1',
        )

        self.assertFalse(gargoyle.is_active('test', request))

        switch.clear_conditions(condition_set=condition_set)

        self.assertTrue(gargoyle.is_active('test', request))

        switch.add_condition(
            condition_set=condition_set,
            field_name='percent',
            condition='50-100',
        )

        self.assertTrue(gargoyle.is_active('test', request))
        
        switch.clear_conditions(condition_set=condition_set)
        switch.add_condition(
            condition_set=condition_set,
            field_name='percent',
            condition='0-50',
        )        
        self.assertFalse(gargoyle.is_active('test', request))
