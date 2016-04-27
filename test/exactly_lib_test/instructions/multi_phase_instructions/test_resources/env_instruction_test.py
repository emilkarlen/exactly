import unittest

from exactly_lib.test_case.os_services import new_with_environ
from exactly_lib_test.instructions.multi_phase_instructions.test_resources.configuration import ConfigurationBase, \
    suite_for_cases
from exactly_lib_test.test_resources.parse import new_source2


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


class TestUnsetExistingVariable(TestCaseBase):
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


class TestUnsetNonExistingVariable(TestCaseBase):
    def runTest(self):
        environ = {'a': 'A'}
        os_services = new_with_environ(environ)
        self.conf.run_test(
                self,
                new_source2('unset non_existing_variable'),
                self.conf.arrangement(os_services=os_services),
                self.conf.expect_success())
        self.assertEqual(environ,
                         {'a': 'A'})


def suite_for(conf: ConfigurationBase) -> unittest.TestSuite:
    return suite_for_cases(conf,
                           [
                               TestSet,
                               TestUnsetExistingVariable,
                               TestUnsetNonExistingVariable,
                           ])
