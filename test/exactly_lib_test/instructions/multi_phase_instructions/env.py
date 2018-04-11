import unittest

from exactly_lib.instructions.multi_phase_instructions import env as sut
from exactly_lib.section_document.element_parsers.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.util.parse.token import HARD_QUOTE_CHAR, SOFT_QUOTE_CHAR
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.common.help.test_resources.check_documentation import suite_for_instruction_documentation
from exactly_lib_test.instructions.multi_phase_instructions.test_resources import \
    instruction_embryo_check as embryo_check
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source, source4
from exactly_lib_test.section_document.test_resources.parse_source_assertions import assert_source
from exactly_lib_test.symbol.data.restrictions.test_resources.concrete_restriction_assertion import \
    is_any_data_type_reference_restrictions
from exactly_lib_test.symbol.data.test_resources import data_symbol_utils as su
from exactly_lib_test.symbol.test_resources.symbol_usage_assertions import matches_reference_2
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_home_and_sds
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        suite_for_instruction_documentation(sut.TheInstructionDocumentation('instruction name')),
        unittest.makeSuite(TestParseSet),
        unittest.makeSuite(TestParseUnset),
        unittest.makeSuite(TestSet),
        unittest.makeSuite(TestSetWithReferencesToExistingEnvVars),
        unittest.makeSuite(TestUnset),
        unittest.makeSuite(TestSetWithSymbolReferences),
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

    def test_variable_name_must_not_be_quoted(self):
        source = source4("'long name' = 'long value'")
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            self.parser.parse(source)

    def test_raise_invalid_argument_if_invalid_quoting(self):
        source = source4("name = 'long value")
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            self.parser.parse(source)


class TestParseUnset(unittest.TestCase):
    parser = sut.EmbryoParser()

    def test_raise_invalid_argument_if_invalid_quoting(self):
        source = source4("unset 'invalid_name")
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            self.parser.parse(source)

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

    def test_unset_identifier_must_not_be_quoted(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            source = source4("'unset' 'long name'")
            self.parser.parse(source)


class TestSet(unittest.TestCase):
    def test_set(self):
        parser = sut.EmbryoParser()
        instruction_embryo = parser.parse(source4('name = value'))
        assert isinstance(instruction_embryo, sut.TheInstructionEmbryo)
        environ = {}
        instruction_embryo.executor.execute(environ, dummy_resolving_env())
        self.assertEqual(environ,
                         {'name': 'value'})


class TestSetWithSymbolReferences(unittest.TestCase):
    def test_set_value_SHOULD_be_able_to_have_symbol_references_in_the_right_hand_side(self):
        variable_name = 'variable_to_assign'

        my_symbol = NameAndValue('my_symbol', 'my symbol value')
        your_symbol = NameAndValue('your_symbol', 'your symbol value')

        value_template = 'pre {MY_SYMBOL} {YOUR_SYMBOL} post'

        expected_evaluated_value_string = value_template.format(
            MY_SYMBOL=my_symbol.value,
            YOUR_SYMBOL=your_symbol.value,
        )
        expected_environ_after_main = {
            variable_name: expected_evaluated_value_string,
        }
        value_source_string = value_template.format(
            MY_SYMBOL=symbol_reference_syntax_for_name(my_symbol.name),
            YOUR_SYMBOL=symbol_reference_syntax_for_name(your_symbol.name),
        )

        source_line = ' {variable_name} = {soft_quote}{source_value_string}{soft_quote}'.format(
            variable_name=variable_name,
            source_value_string=value_source_string,
            soft_quote=SOFT_QUOTE_CHAR,
        )

        following_line = 'following line'
        source = remaining_source(source_line, [following_line])

        arrangement = ArrangementWithSds(
            symbols=SymbolTable({
                my_symbol.name: su.string_constant_container(my_symbol.value),
                your_symbol.name: su.string_constant_container(your_symbol.value),
            }),
        )

        expectation = embryo_check.Expectation(
            main_side_effect_on_environment_variables=asrt.equals(expected_environ_after_main),
            symbol_usages=asrt.matches_sequence([
                matches_reference_2(
                    my_symbol.name,
                    is_any_data_type_reference_restrictions()),
                matches_reference_2(
                    your_symbol.name,
                    is_any_data_type_reference_restrictions()),
            ]),
            source=assert_source(current_line_number=asrt.equals(2),
                                 column_index=asrt.equals(0)),
        )

        parser = sut.EmbryoParser()
        embryo_check.check(self, parser, source, arrangement, expectation)

    def test_set_value_with_hard_quoted_value_SHOULD_skip_symbol_substitution(self):
        variable_name = 'variable_to_assign'

        my_symbol = NameAndValue('my_symbol', 'my symbol value')
        your_symbol = NameAndValue('your_symbol', 'your symbol value')

        value_template = 'pre {MY_SYMBOL} {YOUR_SYMBOL} post'

        value_source_string = value_template.format(
            MY_SYMBOL=symbol_reference_syntax_for_name(my_symbol.name),
            YOUR_SYMBOL=symbol_reference_syntax_for_name(your_symbol.name),
        )
        expected_environ_after_main = {
            variable_name: value_source_string,
        }

        source_line = ' {variable_name} = {hard_quote}{source_value_string}{hard_quote}'.format(
            variable_name=variable_name,
            source_value_string=value_source_string,
            hard_quote=HARD_QUOTE_CHAR,
        )

        following_line = 'following line'
        source = remaining_source(source_line, [following_line])

        arrangement = ArrangementWithSds()

        expectation = embryo_check.Expectation(
            main_side_effect_on_environment_variables=asrt.equals(expected_environ_after_main),
            symbol_usages=asrt.matches_sequence([]),
            source=assert_source(current_line_number=asrt.equals(2),
                                 column_index=asrt.equals(0)),
        )

        parser = sut.EmbryoParser()
        embryo_check.check(self, parser, source, arrangement, expectation)


class TestSetWithReferencesToExistingEnvVars(unittest.TestCase):
    def test_set_value_that_references_an_env_var(self):
        parser = sut.EmbryoParser()
        environ = {'MY_VAR': 'MY_VAL'}
        instruction_embryo = parser.parse(source4('name = ${MY_VAR}'))
        assert isinstance(instruction_embryo, sut.TheInstructionEmbryo)
        instruction_embryo.executor.execute(environ, dummy_resolving_env())
        self.assertEqual(environ,
                         {'name': 'MY_VAL',
                          'MY_VAR': 'MY_VAL'})

    def test_set_value_that_contains_text_and_references_to_env_vars(self):
        parser = sut.EmbryoParser()
        environ = {'MY_VAR': 'MY_VAL',
                   'YOUR_VAR': 'YOUR_VAL'}
        instruction_embryo = parser.parse(source4('name = "pre ${MY_VAR} ${YOUR_VAR} post"'))
        assert isinstance(instruction_embryo, sut.TheInstructionEmbryo)
        instruction_embryo.executor.execute(environ, dummy_resolving_env())
        self.assertEqual(environ,
                         {'name': 'pre MY_VAL YOUR_VAL post',
                          'MY_VAR': 'MY_VAL',
                          'YOUR_VAR': 'YOUR_VAL'})

    def test_a_references_to_a_non_existing_env_var_SHOULD_be_replaced_with_empty_string(self):
        parser = sut.EmbryoParser()
        instruction_embryo = parser.parse(source4('name = ${NON_EXISTING_VAR}'))
        assert isinstance(instruction_embryo, sut.TheInstructionEmbryo)
        environ = {}
        instruction_embryo.executor.execute(environ, dummy_resolving_env())
        self.assertEqual(environ,
                         {'name': ''})


class TestUnset(unittest.TestCase):
    def test_unset(self):
        parser = sut.EmbryoParser()
        instruction_embryo = parser.parse(source4('unset a'))
        assert isinstance(instruction_embryo, sut.TheInstructionEmbryo)
        environ = {'a': 'A', 'b': 'B'}
        instruction_embryo.executor.execute(environ, dummy_resolving_env())
        self.assertEqual(environ,
                         {'b': 'B'})


def dummy_resolving_env() -> PathResolvingEnvironmentPreOrPostSds:
    return PathResolvingEnvironmentPreOrPostSds(fake_home_and_sds())
