from django.contrib.auth.models import User, AnonymousUser
from django.core.cache import cache
from django.http import HttpRequest, Http404
from django.test import TestCase

from gargoyle.models import gargoyle, Switch, SELECTIVE, DISABLED
from gargoyle.decorators import switch_is_active
from gargoyle import autodiscover

autodiscover()

class GargoyleTest(TestCase):
    urls = 'gargoyle.urls'
    
    def setUp(self):
        self.user = User.objects.create(username='foo', email='foo@example.com')
    def test_builtin_discovery(self):
        # TODO: this test should just ensure we've registered our builtins
        self.assertEquals(len(gargoyle._registry), 2)

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
        self.assertTrue(gargoyle.is_active('test_user', user))

        user = User(pk=8771)
        self.assertFalse(gargoyle.is_active('test_user', user))

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
        self.assertFalse(gargoyle.is_active('test_user', user))

        user = User(pk=8771, username='foo')
        self.assertTrue(gargoyle.is_active('test_user', user))

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
            field_name='ip_address',
        )

        switch.add_condition(
            condition_set=condition_set,
            field_name='percent',
            condition='0-50',
        )

        self.assertRaises(Http404, test, request)

    def test_global(self):
        gargoyle['test_for_all'] = {}

        self.assertTrue(gargoyle.is_active('test_for_all'))

        gargoyle['test_for_all'] = {'auth.user': {'username': ['dcramer']}}

        self.assertFalse(gargoyle.is_active('test_for_all'))

        gargoyle['test_for_all'] = {'auth.user': {'username': ['dcramer']}, 'global': True}

        self.assertTrue(gargoyle.is_active('test_for_all'))

    def test_disable(self):
        gargoyle['test_disable'] = {'global': False}

        self.assertFalse(gargoyle.is_active('test_disable'))

        self.assertFalse(gargoyle.is_active('test_disable', self.user))

    def test_expiration(self):
        gargoyle['test_expiration'] = {'global': False}

        self.assertFalse(gargoyle.is_active('test_expiration'))

        Switch.objects.filter(key='test_expiration').update(value={})

        # cache shouldn't have expired
        self.assertFalse(gargoyle.is_active('test_expiration'))

        # in memory cache shouldnt have expired
        cache.delete(gargoyle.cache_key)
        self.assertFalse(gargoyle.is_active('test_expiration'))

        # any request should expire the in memory cache
        self.client.get('/')

        self.assertTrue(gargoyle.is_active('test_expiration'))

    def test_anonymous_user(self):
        gargoyle['test_anonymous_user'] = {'global': False}

        user = AnonymousUser()

        self.assertFalse(gargoyle.is_active('test_anonymous_user', user))

        gargoyle['test_anonymous_user'] = {'auth.user': {'percent': [1, 10]}}

        self.assertFalse(gargoyle.is_active('test_anonymous_user', user))

        gargoyle['test_anonymous_user'] = {}

        self.assertTrue(gargoyle.is_active('test_anonymous_user', user))

        gargoyle['test_anonymous_user'] = {'auth.user': {'is_authenticated': False}}

        self.assertTrue(gargoyle.is_active('test_anonymous_user', user))

        gargoyle['test_anonymous_user'] = {'auth.user': {'percent': [1, 10], 'is_authenticated': False}}

        self.assertTrue(gargoyle.is_active('test_anonymous_user', user))

    def test_ip_address(self):
        request = HttpRequest()
        request.META['REMOTE_ADDR'] = '192.168.1.1'

        self.assertFalse(gargoyle.is_active('test_ip_address', request))

        gargoyle['test_ip_address'] = {'ip': {'ip_address': ['192.168.1.1']}}

        self.assertTrue(gargoyle.is_active('test_ip_address', request))

        gargoyle['test_ip_address'] = {'ip': {'ip_address': ['127.0.1.1']}}

        self.assertFalse(gargoyle.is_active('test_ip_address', request))

        gargoyle['test_ip_address'] = {}

        self.assertTrue(gargoyle.is_active('test_ip_address', request))

        gargoyle['test_ip_address'] = {'ip': {'percent': [[50, 100]]}}

        self.assertTrue(gargoyle.is_active('test_ip_address', request))
        
        gargoyle['test_ip_address'] = {'ip': {'percent': [[0, 50]]}}
        
        self.assertFalse(gargoyle.is_active('test_ip_address', request))
