import unittest
from nose.tools import *

from gargoyle.singleton import gargoyle
from gargoyle.testutils import switches
from gargoyle.models import Switch


class TestDecorator(unittest.TestCase):

    def setUp(self):
        gargoyle.register(Switch('foo'))

    def tearDown(self):
        gargoyle.flush()

    @switches(foo=True)
    def with_decorator(self):
        return gargoyle.active('foo')

    def without_decorator(self):
        return gargoyle.active('foo')

    def test_decorator_overrides_switch_setting(self):
        eq_(self.without_decorator(), False)
        eq_(self.with_decorator(), True)

    def test_context_manager_overrides_swich_setting(self):
        eq_(gargoyle.active('foo'), False)

        with switches(foo=True):
            eq_(gargoyle.active('foo'), True)
