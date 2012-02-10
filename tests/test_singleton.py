import unittest
from nose.tools import *
import mock

from gargoyle.settings import manager
import gargoyle.models


class TestGargoyle(unittest.TestCase):

    other_engine = dict()

    def test_gargoyle_global_is_a_switch_manager(self):
        reload(gargoyle.singleton)
        self.assertIsInstance(gargoyle.singleton.gargoyle,
                              gargoyle.models.Manager)

    def test_consructs_manager_with_storage_engine_from_settings(self):
        with mock.patch('gargoyle.models.Manager') as init:
            init.return_value = None
            reload(gargoyle.singleton)
            expected = ((), {'storage': manager.storage_engine})
            eq_(init.call_args, expected)

    def test_can_change_storage_engine_before_importing(self):
        with mock.patch('gargoyle.models.Manager') as init:
            init.return_value = None
            manager.storage_engine = self.other_engine
            reload(gargoyle.singleton)
            expected = ((), dict(storage=self.other_engine))
            eq_(init.call_args, expected)
