import unittest

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from shellcheck_lib.instructions.multi_phase_instructions import env as sut
from shellcheck_lib.test_case.os_services import new_with_environ
from shellcheck_lib_test.instructions.test_resources.check_description import suite_for_description
from shellcheck_lib_test.instructions.test_resources.utils import new_source2


def identity(x): return x


class TestParseSet(unittest.TestCase):
    parser = sut.Parser(identity)

    def test_fail_when_there_is_no_arguments(self):
        source = new_source2('')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            self.parser.apply(source)

    def test_fail_when_there_is_more_than_three_argument(self):
        source = new_source2('argument1 = argument3 argument4')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            self.parser.apply(source)

    def test_succeed_when_there_is_exactly_one_assignment(self):
        source = new_source2('name = value')
        self.parser.apply(source)

    def test_both_name_and_value_can_be_shell_quoted(self):
        source = new_source2("'long name' = 'long value'")
        self.parser.apply(source)


class TestParseUnset(unittest.TestCase):
    parser = sut.Parser(identity)

    def test_fail_when_there_is_no_arguments(self):
        source = new_source2('unset')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            self.parser.apply(source)

    def test_fail_when_there_is_more_than_one_argument(self):
        source = new_source2('unset name superfluous')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            self.parser.apply(source)

    def test_succeed_when_there_is_exactly_one_argument(self):
        source = new_source2('unset name')
        self.parser.apply(source)

    def test_all_parts_may_be_shell_quoted(self):
        source = new_source2("'unset' 'long name'")
        self.parser.apply(source)


class TestSet(unittest.TestCase):
    def test_set(self):
        parser = sut.Parser(identity)
        executor = parser.apply(new_source2('name = value'))
        assert isinstance(executor, sut.Executor)
        environ = {}
        os_services = new_with_environ(environ)
        executor.execute(os_services)
        self.assertEqual(environ,
                         {'name': 'value'})


class TestUnset(unittest.TestCase):
    def test_unset(self):
        parser = sut.Parser(identity)
        executor = parser.apply(new_source2('unset a'))
        assert isinstance(executor, sut.Executor)
        environ = {'a': 'A', 'b': 'B'}
        os_services = new_with_environ(environ)
        executor.execute(os_services)
        self.assertEqual(environ,
                         {'b': 'B'})


def suite():
    return unittest.TestSuite([
        suite_for_description(sut.TheDescription('instruction name')),
        unittest.makeSuite(TestParseSet),
        unittest.makeSuite(TestParseUnset),
        unittest.makeSuite(TestSet),
        unittest.makeSuite(TestUnset),
    ])
