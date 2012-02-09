import unittest
from nose.tools import *
import mock

from gargoyle.settings import manager
import gargoyle.models


class TestGargoyle(unittest.TestCase):

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
