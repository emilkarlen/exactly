import unittest

from exactly_lib.execution import partial_execution as sut
from exactly_lib_test.execution.partial_execution.test_resources.basic import py3_test, \
    TestCaseWithCommonDefaultInstructions, Result


class Test(unittest.TestCase):
    def test_keep_execution_directory_root(self):
        py3_test(
                self,
                test_case_that_does_nothing(),
                execution_directory_structure_exists,
                is_keep_execution_directory_root=True)

    def test_do_not_keep_execution_directory_root(self):
        py3_test(
                self,
                test_case_that_does_nothing(),
                execution_directory_structure_does_not_exist,
                is_keep_execution_directory_root=False)


def execution_directory_structure_exists(put: unittest.TestCase,
                                         actual: Result):
    _common_assertions(actual, put)
    put.assertTrue(actual.partial_result.execution_directory_structure.root_dir.is_dir())


def execution_directory_structure_does_not_exist(put: unittest.TestCase,
                                                 actual: Result):
    _common_assertions(actual, put)
    put.assertFalse(actual.partial_result.execution_directory_structure.root_dir.exists())


def _common_assertions(actual, put):
    put.assertTrue(actual.partial_result.has_execution_directory_structure,
                   'EDS is expected to have been created')


def test_case_that_does_nothing() -> sut.TestCase:
    return TestCaseWithCommonDefaultInstructions().test_case


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(Test))
    return ret_val


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
