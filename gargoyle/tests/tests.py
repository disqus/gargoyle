from django.contrib.auth.models import User, AnonymousUser
from django.core.cache import cache
from django.http import HttpRequest, Http404
from django.test import TestCase

from gargoyle.builtins import IPAddressConditionSet, UserConditionSet
from gargoyle.models import Switch, SwitchManager, SELECTIVE, DISABLED, GLOBAL
from gargoyle.decorators import switch_is_active

class GargoyleTest(TestCase):
    urls = 'gargoyle.tests.urls'
    
    def setUp(self):
        self.user = User.objects.create(username='foo', email='foo@example.com')
        self.gargoyle = SwitchManager(Switch, key='key', value='value', instances=True)
        self.gargoyle.register(UserConditionSet(User))
        self.gargoyle.register(IPAddressConditionSet())

    def test_builtin_registration(self):
        self.assertTrue('gargoyle.builtins.UserConditionSet(auth.user)' in self.gargoyle._registry)
        self.assertTrue('gargoyle.builtins.IPAddressConditionSet' in self.gargoyle._registry)
        self.assertEquals(len(list(self.gargoyle.get_condition_sets())), 2, self.gargoyle)
        
    def test_user(self):
        condition_set = 'gargoyle.builtins.UserConditionSet(auth.user)'
        
        # we need a better API for this (model dict isnt cutting it)
        switch = Switch.objects.create(
            key='test',
            status=SELECTIVE,
        )
        switch = self.gargoyle['test']
        
        switch.add_condition(
            condition_set=condition_set,
            field_name='percent',
            condition='0-50',
        )

        user = User(pk=5)
        self.assertTrue(self.gargoyle.is_active('test', user))

        user = User(pk=8771)
        self.assertFalse(self.gargoyle.is_active('test', user))
        
        switch.add_condition(
            condition_set=condition_set,
            field_name='is_staff',
            condition='1',
        )

        user = User(pk=8771, is_staff=True)
        self.assertTrue(self.gargoyle.is_active('test', user))

        user = User(pk=8771, is_superuser=True)
        self.assertFalse(self.gargoyle.is_active('test', user))

        switch.add_condition(
            condition_set=condition_set,
            field_name='is_superuser',
            condition='1',
        )
        
        user = User(pk=8771, is_superuser=True)
        self.assertTrue(self.gargoyle.is_active('test', user))

    def test_exclusions(self):
        condition_set = 'gargoyle.builtins.UserConditionSet(auth.user)'
        
        switch = Switch.objects.create(
            key='test',
            status=SELECTIVE,
        )
        switch = self.gargoyle['test']
        
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
        self.assertFalse(self.gargoyle.is_active('test', user))

        user = User(pk=8771, username='foo')
        self.assertTrue(self.gargoyle.is_active('test', user))

    def test_decorator_for_user(self):
        condition_set = 'gargoyle.builtins.UserConditionSet(auth.user)'
        
        switch = Switch.objects.create(
            key='test',
            status=DISABLED,
        )
        switch = self.gargoyle['test']
        
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
        switch = self.gargoyle['test']
        
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

    def test_decorator_with_redirect(self):
        condition_set = 'gargoyle.builtins.UserConditionSet(auth.user)'
        
        switch = Switch.objects.create(
            key='test',
            status=DISABLED,
        )
        switch = self.gargoyle['test']

        request = HttpRequest()
        request.user = self.user
        
        @switch_is_active('test', redirect_to='/foo')
        def test(request):
            return True

        response = test(request)
        self.assertTrue(response.status_code, 302)
        self.assertTrue('Location' in response)
        self.assertTrue(response['Location'], '/foo')

        @switch_is_active('test', redirect_to='gargoyle_test_foo')
        def test(request):
            return True

        response = test(request)
        self.assertTrue(response.status_code, 302)
        self.assertTrue('Location' in response)
        self.assertTrue(response['Location'], '')

    def test_global(self):
        condition_set = 'gargoyle.builtins.UserConditionSet(auth.user)'
        
        switch = Switch.objects.create(
            key='test',
            status=SELECTIVE,
        )
        switch = self.gargoyle['test']

        self.assertTrue(self.gargoyle.is_active('test'))
        self.assertTrue(self.gargoyle.is_active('test', self.user))
        
        switch.status = GLOBAL
        switch.save()

        self.assertTrue(self.gargoyle.is_active('test'))
        self.assertTrue(self.gargoyle.is_active('test', self.user))

    def test_disable(self):
        switch = Switch.objects.create(key='test')
        
        switch = self.gargoyle['test']
        
        switch.status = DISABLED
        switch.save()

        self.assertFalse(self.gargoyle.is_active('test'))

        self.assertFalse(self.gargoyle.is_active('test', self.user))

    def test_deletion(self):
        switch = Switch.objects.create(key='test')
        
        switch = self.gargoyle['test']

        self.assertTrue('test' in self.gargoyle)
        
        switch.delete()
        
        self.assertFalse('test' in self.gargoyle)

    def test_expiration(self):
        switch = Switch.objects.create(key='test')
        
        switch = self.gargoyle['test']
        
        switch.status = DISABLED
        switch.save()

        self.assertFalse(self.gargoyle.is_active('test'))

        Switch.objects.filter(key='test').update(value={}, status=SELECTIVE)

        # cache shouldn't have expired
        self.assertFalse(self.gargoyle.is_active('test'))

        # in memory cache shouldnt have expired
        cache.delete(self.gargoyle.cache_key)
        self.assertFalse(self.gargoyle.is_active('test'))
        switch.status, switch.value = SELECTIVE, {}
        # Ensure post save gets sent
        self.gargoyle._post_save(sender=None, instance=switch, created=False)

        # any request should expire the in memory cache
        self.client.get('/')
        
        self.assertTrue(self.gargoyle.is_active('test'))

    def test_anonymous_user(self):
        condition_set = 'gargoyle.builtins.UserConditionSet(auth.user)'

        switch = Switch.objects.create(key='test')
        
        switch = self.gargoyle['test']
        
        switch.status = SELECTIVE
        switch.save()
        
        user = AnonymousUser()

        self.assertTrue(self.gargoyle.is_active('test', user))

        switch.add_condition(
            condition_set=condition_set,
            field_name='percent',
            condition='1-10',
        )

        self.assertFalse(self.gargoyle.is_active('test', user))

        switch.clear_conditions(
            condition_set=condition_set,
        )

        self.assertTrue(self.gargoyle.is_active('test', user))

        switch.add_condition(
            condition_set=condition_set,
            field_name='is_anonymous',
            condition='1',
        )

        self.assertTrue(self.gargoyle.is_active('test', user))

        switch.add_condition(
            condition_set=condition_set,
            field_name='percent',
            condition='1-10',
        )

        self.assertTrue(self.gargoyle.is_active('test', user))

    def test_ip_address(self):
        condition_set = 'gargoyle.builtins.IPAddressConditionSet'
        
        switch = Switch.objects.create(
            key='test',
            status=SELECTIVE,
        )
        switch = self.gargoyle['test']


        request = HttpRequest()
        request.META['REMOTE_ADDR'] = '192.168.1.1'

        self.assertTrue(self.gargoyle.is_active('test', request))

        switch.add_condition(
            condition_set=condition_set,
            field_name='ip_address',
            condition='192.168.1.1',
        )

        self.assertTrue(self.gargoyle.is_active('test', request))

        switch.clear_conditions(
            condition_set=condition_set,
        )
        switch.add_condition(
            condition_set=condition_set,
            field_name='ip_address',
            condition='127.0.0.1',
        )

        self.assertFalse(self.gargoyle.is_active('test', request))

        switch.clear_conditions(
            condition_set=condition_set,
        )

        self.assertTrue(self.gargoyle.is_active('test', request))

        switch.add_condition(
            condition_set=condition_set,
            field_name='percent',
            condition='50-100',
        )

        self.assertTrue(self.gargoyle.is_active('test', request))
        
        switch.clear_conditions(
            condition_set=condition_set,
        )
        switch.add_condition(
            condition_set=condition_set,
            field_name='percent',
            condition='0-50',
        )        
        self.assertFalse(self.gargoyle.is_active('test', request))

    def test_to_dict(self):
        condition_set = 'gargoyle.builtins.IPAddressConditionSet'
        
        switch = Switch.objects.create(
            label='my switch',
            description='foo bar baz',
            key='test',
            status=SELECTIVE,
        )
        
        switch.add_condition(
            manager=self.gargoyle,
            condition_set=condition_set,
            field_name='ip_address',
            condition='192.168.1.1',
        )
        
        result = switch.to_dict(self.gargoyle)
        
        self.assertTrue('label' in result)
        self.assertEquals(result['label'], 'my switch')

        self.assertTrue('status' in result)
        self.assertEquals(result['status'], SELECTIVE)

        self.assertTrue('description' in result)
        self.assertEquals(result['description'], 'foo bar baz')
        
        self.assertTrue('key' in result)
        self.assertEquals(result['key'], 'test')

        self.assertTrue('conditions' in result)
        self.assertEquals(len(result['conditions']), 1)

        condition = result['conditions'][0]
        self.assertTrue('id' in condition)
        self.assertEquals(condition['id'], condition_set)
        self.assertTrue('label' in condition)
        self.assertEquals(condition['label'], 'IP Address')
        self.assertTrue('conditions' in condition)
        self.assertEquals(len(condition['conditions']), 1)
        
        inner_condition = condition['conditions'][0]
        self.assertEquals(len(inner_condition), 4)
        self.assertTrue(inner_condition[0], 'ip_address')
        self.assertTrue(inner_condition[1], '192.168.1.1')
        self.assertTrue(inner_condition[2], '192.168.1.1')
        self.assertFalse(inner_condition[3])
