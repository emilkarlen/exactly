import unittest

from shellcheck_lib.test_case.os_services import new_with_environ
from shellcheck_lib_test.instructions.multi_phase_instructions.test_resources.configuration import ConfigurationBase, \
    suite_for_cases
from shellcheck_lib_test.test_resources.parse import new_source2


class TestCaseBase(unittest.TestCase):
    def __init__(self, conf: ConfigurationBase):
        super().__init__()
        self.conf = conf


class TestSet(TestCaseBase):
    def runTest(self):
        environ = {}
        os_services = new_with_environ(environ)
        self.conf.run_test(
                self,
                new_source2('name = value'),
                self.conf.arrangement(os_services=os_services),
                self.conf.expect_success())
        self.assertEqual(environ,
                         {'name': 'value'})


class TestUnset(TestCaseBase):
    def runTest(self):
        environ = {'a': 'A', 'b': 'B'}
        os_services = new_with_environ(environ)
        self.conf.run_test(
                self,
                new_source2('unset a'),
                self.conf.arrangement(os_services=os_services),
                self.conf.expect_success())
        self.assertEqual(environ,
                         {'b': 'B'})


def suite_for(conf: ConfigurationBase) -> unittest.TestSuite:
    return suite_for_cases(conf,
                           [
                               TestSet,
                               TestUnset,
                           ])
