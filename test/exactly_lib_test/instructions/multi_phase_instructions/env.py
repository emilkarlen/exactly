import unittest

from exactly_lib.instructions.multi_phase_instructions import env as sut
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib_test.instructions.test_resources.check_description import suite_for_instruction_documentation
from exactly_lib_test.test_resources.parse import source4


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        suite_for_instruction_documentation(sut.TheInstructionDocumentation('instruction name')),
        unittest.makeSuite(TestParseSet),
        unittest.makeSuite(TestParseUnset),
        unittest.makeSuite(TestSet),
        unittest.makeSuite(TestSetWithReferencesToExistingEnvVars),
        unittest.makeSuite(TestUnset),
    ])


class TestParseSet(unittest.TestCase):
    parser = sut.EmbryoParser()

    def test_fail_when_there_is_no_arguments(self):
        source = source4('')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            self.parser.parse(source)

    def test_fail_when_there_is_more_than_three_argument(self):
        source = source4('argument1 = argument3 argument4')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            self.parser.parse(source)

    def test_succeed_when_there_is_exactly_one_assignment(self):
        source = source4('name = value')
        self.parser.parse(source)

    def test_both_name_and_value_can_be_shell_quoted(self):
        source = source4("'long name' = 'long value'")
        self.parser.parse(source)


class TestParseUnset(unittest.TestCase):
    parser = sut.EmbryoParser()

    def test_fail_when_there_is_no_arguments(self):
        source = source4('unset')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            self.parser.parse(source)

    def test_fail_when_there_is_more_than_one_argument(self):
        source = source4('unset name superfluous')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            self.parser.parse(source)

    def test_succeed_when_there_is_exactly_one_argument(self):
        source = source4('unset name')
        self.parser.parse(source)

    def test_all_parts_may_be_shell_quoted(self):
        source = source4("'unset' 'long name'")
        self.parser.parse(source)


class TestSet(unittest.TestCase):
    def test_set(self):
        parser = sut.EmbryoParser()
        instruction_embryo = parser.parse(source4('name = value'))
        assert isinstance(instruction_embryo, sut.TheInstructionEmbryo)
        environ = {}
        instruction_embryo.executor.execute(environ)
        self.assertEqual(environ,
                         {'name': 'value'})


class TestSetWithReferencesToExistingEnvVars(unittest.TestCase):
    def test_set_value_that_references_an_env_var(self):
        parser = sut.EmbryoParser()
        environ = {'MY_VAR': 'MY_VAL'}
        instruction_embryo = parser.parse(source4('name = ${MY_VAR}'))
        assert isinstance(instruction_embryo, sut.TheInstructionEmbryo)
        instruction_embryo.executor.execute(environ)
        self.assertEqual(environ,
                         {'name': 'MY_VAL',
                          'MY_VAR': 'MY_VAL'})

    def test_set_value_that_contains_text_and_references_to_env_vars(self):
        parser = sut.EmbryoParser()
        environ = {'MY_VAR': 'MY_VAL',
                   'YOUR_VAR': 'YOUR_VAL'}
        instruction_embryo = parser.parse(source4('name = "pre ${MY_VAR} ${YOUR_VAR} post"'))
        assert isinstance(instruction_embryo, sut.TheInstructionEmbryo)
        instruction_embryo.executor.execute(environ)
        self.assertEqual(environ,
                         {'name': 'pre MY_VAL YOUR_VAL post',
                          'MY_VAR': 'MY_VAL',
                          'YOUR_VAR': 'YOUR_VAL'})

    def test_a_references_to_a_non_existing_env_var_SHOULD_be_replaced_with_empty_string(self):
        parser = sut.EmbryoParser()
        instruction_embryo = parser.parse(source4('name = ${NON_EXISTING_VAR}'))
        assert isinstance(instruction_embryo, sut.TheInstructionEmbryo)
        environ = {}
        instruction_embryo.executor.execute(environ)
        self.assertEqual(environ,
                         {'name': ''})


class TestUnset(unittest.TestCase):
    def test_unset(self):
        parser = sut.EmbryoParser()
        instruction_embryo = parser.parse(source4('unset a'))
        assert isinstance(instruction_embryo, sut.TheInstructionEmbryo)
        environ = {'a': 'A', 'b': 'B'}
        instruction_embryo.executor.execute(environ)
        self.assertEqual(environ,
                         {'b': 'B'})
