import unittest

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from shellcheck_lib.test_case.os_services import new_with_environ
from shellcheck_lib_test.instructions import utils
from shellcheck_lib_test.instructions.setup.test_resources.instruction_check import Flow, TestCaseBase
from shellcheck_lib.instructions.setup import env as sut
from shellcheck_lib_test.instructions.utils import new_source


class TestParseSet(unittest.TestCase):
    def test_fail_when_there_is_no_arguments(self):
        source = utils.new_source('instruction-name', '')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.Parser().apply(source)

    def test_fail_when_there_is_more_than_three_argument(self):
        source = utils.new_source('instruction-name', 'argument1 = argument3 argument4')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.Parser().apply(source)

    def test_succeed_when_there_is_exactly_one_assignment(self):
        source = utils.new_source('instruction-name', 'name = value')
        sut.Parser().apply(source)

    def test_both_name_and_value_can_be_shell_quoted(self):
        source = utils.new_source('instruction-name', "'long name' = 'long value'")
        sut.Parser().apply(source)


class TestParseUnset(unittest.TestCase):
    def test_fail_when_there_is_no_arguments(self):
        source = utils.new_source('instruction-name', 'unset')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.Parser().apply(source)

    def test_fail_when_there_is_more_than_one_argument(self):
        source = utils.new_source('instruction-name', 'unset name superfluous')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.Parser().apply(source)

    def test_succeed_when_there_is_exactly_one_argument(self):
        source = utils.new_source('instruction-name', 'unset name')
        sut.Parser().apply(source)

    def test_all_parts_may_be_shell_quoted(self):
        source = utils.new_source('instruction-name', "'unset' 'long name'")
        sut.Parser().apply(source)


class TestSet(TestCaseBase):
    def test_set(self):
        environ = {}
        os_services = new_with_environ(environ)
        self._check(
            Flow(sut.Parser(),
                 os_services=os_services),
            new_source('instruction-name',
                       'name = value'))
        self.assertEqual(environ,
                         {'name': 'value'})


class TestUnset(TestCaseBase):
    def test_unset(self):
        environ = {'a': 'A', 'b': 'B'}
        os_services = new_with_environ(environ)
        self._check(
            Flow(sut.Parser(),
                 os_services=os_services),
            new_source('instruction-name',
                       'unset a'))
        self.assertEqual(environ,
                         {'b': 'B'})


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestParseSet))
    ret_val.addTest(unittest.makeSuite(TestSet))
    ret_val.addTest(unittest.makeSuite(TestParseUnset))
    ret_val.addTest(unittest.makeSuite(TestUnset))
    return ret_val


if __name__ == '__main__':
    unittest.main()
