import unittest

from exactly_lib.instructions.multi_phase import env as sut
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.type_val_deps.envs.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.process_execution import execution_elements
from exactly_lib.util.str_.formatter import StringFormatter
from exactly_lib_test.common.help.test_resources.check_documentation import suite_for_instruction_documentation
from exactly_lib_test.instructions.multi_phase.test_resources import \
    instruction_embryo_check as embryo_check
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.section_document.test_resources.parse_source import source4
from exactly_lib_test.section_document.test_resources.parse_source_assertions import assert_source
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.tcfs.test_resources.paths import fake_tcds
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.test_resources.strings import WithToString
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.types.string.test_resources.string import StringConstantSymbolContext
from exactly_lib_test.util.process_execution.test_resources.proc_exe_env import proc_exe_env_for_test
from exactly_lib_test.util.test_resources.quoting import surrounded_by_soft_quotes, surrounded_by_hard_quotes, \
    Surrounded


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        suite_for_instruction_documentation(sut.TheInstructionDocumentation('instruction name')),
        unittest.makeSuite(TestInvalidSyntaxOfSetShouldBeDetected),
        unittest.makeSuite(TestInvalidSyntaxOfUnsetShouldBeDetected),
        unittest.makeSuite(TestSet),
        unittest.makeSuite(TestSetWithReferencesToExistingEnvVars),
        unittest.makeSuite(TestUnset),
    ])


class TestInvalidSyntaxOfSetShouldBeDetected(unittest.TestCase):
    parser = sut.EmbryoParser()

    def test_fail_when_there_is_no_arguments(self):
        source = source4('')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            self.parser.parse(ARBITRARY_FS_LOCATION_INFO, source)

    def test_fail_when_there_is_more_than_three_argument(self):
        source = source4('argument1 = argument3 argument4')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            self.parser.parse(ARBITRARY_FS_LOCATION_INFO, source)

    def test_variable_name_must_not_be_quoted(self):
        source = source4("'long name' = 'long value'")
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            self.parser.parse(ARBITRARY_FS_LOCATION_INFO, source)

    def test_raise_invalid_argument_if_invalid_quoting(self):
        source = source4("name = 'long value")
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            self.parser.parse(ARBITRARY_FS_LOCATION_INFO, source)


class TestInvalidSyntaxOfUnsetShouldBeDetected(unittest.TestCase):
    parser = sut.EmbryoParser()

    def test_raise_invalid_argument_if_invalid_quoting(self):
        source = source4("unset 'invalid_name")
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            self.parser.parse(ARBITRARY_FS_LOCATION_INFO, source)

    def test_fail_when_there_is_no_arguments(self):
        source = source4(sut.UNSET_IDENTIFIER)
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            self.parser.parse(ARBITRARY_FS_LOCATION_INFO, source)

    def test_fail_when_there_is_more_than_one_argument(self):
        source = source4('unset name superfluous')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            self.parser.parse(ARBITRARY_FS_LOCATION_INFO, source)

    def test_unset_identifier_must_not_be_quoted(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            source = source4("'unset' 'long name'")
            self.parser.parse(ARBITRARY_FS_LOCATION_INFO, source)


class TestSet(unittest.TestCase):
    def test_constant_string_value(self):
        # ACT & ASSERT #
        var = NameAndValue('name', 'value')

        _CHECKER.check__w_source_variants(
            self,
            syntax_for_set__nav(var),
            embryo_check.ArrangementWithSds(
                process_execution_settings=
                proc_exe_env_for_test(
                    environ={}
                )
            ),
            embryo_check.Expectation(
                main_result=asrt.is_none,
                main_side_effect_on_environment_variables=asrt.equals(
                    {
                        var.name: var.value
                    }
                )
            )
        )

    def test_variable_with_same_name_as_unset_keyword(self):
        # ACT & ASSERT #
        var = NameAndValue(sut.UNSET_IDENTIFIER, 'value')

        _CHECKER.check__w_source_variants(
            self,
            syntax_for_set__nav(var),
            embryo_check.ArrangementWithSds(
                process_execution_settings=
                proc_exe_env_for_test(
                    environ={}
                )
            ),
            embryo_check.Expectation(
                main_result=asrt.is_none,
                main_side_effect_on_environment_variables=asrt.equals(
                    {
                        var.name: var.value
                    }
                )
            )
        )

    def test_argument_elements_on_multiple_lines(self):
        # ACT & ASSERT #
        var = NameAndValue('name', 'value')

        sf = StringFormatter({
            'name': var.name,
            'quoted_value': surrounded_by_hard_quotes(var.value)
        })

        cases = [
            NameAndValue(
                'value on following line',
                sf.format('{name} = \n {quoted_value}')
            ),
            NameAndValue(
                'equals on following line',
                sf.format('{name} \n = {quoted_value}')
            ),
            NameAndValue(
                'name on following line',
                sf.format('\n {name} = {quoted_value}')
            ),
            NameAndValue(
                'all elements on separate lines',
                sf.format('\n {name} \n = \n {quoted_value}')
            ),
        ]

        environ__before = {}
        environ__after = {var.name: var.value}

        expectation = asrt.equals(environ__after)

        for case in cases:
            with self.subTest(case.name):
                # ACT & ASSERT #
                _CHECKER.check__w_source_variants(
                    self,
                    case.value,
                    embryo_check.ArrangementWithSds(
                        process_execution_settings=
                        proc_exe_env_for_test(
                            environ=environ__before
                        )
                    ),
                    embryo_check.Expectation(
                        main_result=asrt.is_none,
                        main_side_effect_on_environment_variables=expectation
                    )
                )

    def test_multi_line_value(self):
        # ARRANGE #
        var = NameAndValue('name', 'a\nmulti\nline\nvalue\n')
        environ__before = {}
        environ__after = {var.name: var.value}

        # ACT & ASSERT #

        cases = [
            NameAndValue('soft quoting',
                         surrounded_by_soft_quotes(var.value)
                         ),
            NameAndValue('hard quoting',
                         surrounded_by_hard_quotes(var.value)
                         ),
        ]

        for case in cases:
            with self.subTest(case.name):
                _CHECKER.check__w_source_variants(
                    self,
                    syntax_for_set(var.name, case.value),
                    embryo_check.ArrangementWithSds(
                        process_execution_settings=
                        proc_exe_env_for_test(
                            environ=environ__before
                        )
                    ),
                    embryo_check.Expectation(
                        main_result=asrt.is_none,
                        main_side_effect_on_environment_variables=asrt.equals(
                            environ__after)
                    )
                )

    def test_WHEN_env_contains_the_var_being_set_THEN_its_value_SHOULD_be_replaced(self):
        # ACT & ASSERT #
        var_name = 'ENV_VAR'
        value_before = 'before'
        value_after = 'after'

        environ__before = {
            var_name: value_before
        }

        environ__after = {
            var_name: value_after
        }

        _CHECKER.check__w_source_variants(
            self,
            syntax_for_set(var_name, value_after),
            embryo_check.ArrangementWithSds(
                process_execution_settings=
                proc_exe_env_for_test(
                    environ=environ__before
                )
            ),
            embryo_check.Expectation(
                main_result=asrt.is_none,
                main_side_effect_on_environment_variables=asrt.equals(
                    environ__after
                )
            )
        )

    def test_value_SHOULD_be_able_to_have_symbol_references(self):
        # ARRANGE #

        variable_name = 'variable_to_assign'

        my_symbol = StringConstantSymbolContext('my_symbol', 'my symbol value')
        your_symbol = StringConstantSymbolContext('your_symbol', 'your symbol value')

        value_template = 'pre {MY_SYMBOL} {YOUR_SYMBOL} post'

        expected_evaluated_value_string = value_template.format(
            MY_SYMBOL=my_symbol.str_value,
            YOUR_SYMBOL=your_symbol.str_value,
        )
        expected_environ_after_main = {
            variable_name: expected_evaluated_value_string,
        }
        value_source_string = value_template.format(
            MY_SYMBOL=symbol_reference_syntax_for_name(my_symbol.name),
            YOUR_SYMBOL=symbol_reference_syntax_for_name(your_symbol.name),
        )

        source_line = syntax_for_set(variable_name,
                                     surrounded_by_soft_quotes(value_source_string))

        # ACT & ASSERT #

        _CHECKER.check__w_source_variants(
            self,
            source_line,
            ArrangementWithSds(
                symbols=
                SymbolContext.symbol_table_of_contexts([my_symbol, your_symbol]),
                process_execution_settings=
                execution_elements.with_environ_copy({}),
            ),
            embryo_check.Expectation(
                main_side_effect_on_environment_variables=asrt.equals(expected_environ_after_main),
                symbol_usages=asrt.matches_sequence([
                    my_symbol.usage_assertion__any_data_type,
                    your_symbol.usage_assertion__any_data_type,
                ]),
                source=assert_source(current_line_number=asrt.equals(2),
                                     column_index=asrt.equals(0)),
            ),
        )

    def test_value_with_hard_quoted_value_SHOULD_skip_symbol_substitution(self):
        # ARRANGE #

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

        source_line = syntax_for_set(variable_name,
                                     surrounded_by_hard_quotes(value_source_string))

        # ACT & ASSERT #

        _CHECKER.check__w_source_variants(
            self,
            source_line,
            ArrangementWithSds(
                process_execution_settings=
                execution_elements.with_environ_copy({}),
            ),
            embryo_check.Expectation(
                main_side_effect_on_environment_variables=asrt.equals(expected_environ_after_main),
                symbol_usages=asrt.matches_sequence([]),
            ),
        )


class TestSetWithReferencesToExistingEnvVars(unittest.TestCase):
    def test_set_value_that_references_an_env_var(self):
        # ARRANGE #

        existing_env_var = NameAndValue('MY_VAR', 'MY_VAL')
        defined_env_var = NameAndValue('name', existing_env_var.value)

        environ__before = {
            existing_env_var.name: existing_env_var.value,
        }
        environ__after = {
            defined_env_var.name: defined_env_var.value,
            existing_env_var.name: existing_env_var.value,
        }

        # ACT & ASSERT #

        _CHECKER.check__w_source_variants(
            self,
            syntax_for_set(defined_env_var.name,
                           env_var_ref_syntax(existing_env_var.name)),
            arrangement=
            ArrangementWithSds(
                process_execution_settings=
                execution_elements.with_environ_copy(environ__before),
            ),
            expectation=
            embryo_check.Expectation(
                main_side_effect_on_environment_variables=asrt.equals(environ__after),
            )
        )

    def test_set_value_that_contains_text_and_references_to_env_vars(self):
        # ARRANGE #

        my_var = NameAndValue('MY_VAR', 'MY_VAL')
        your_var = NameAndValue('YOUR_VAR', 'YOUR_VAL')
        var_to_set_name = 'name'

        value_template = 'pre {my_var} {your_var} post'

        source_value_argument = surrounded_by_soft_quotes(
            value_template.format(
                my_var=env_var_ref_syntax(my_var.name),
                your_var=env_var_ref_syntax(your_var.name),
            )
        )

        source = syntax_for_set(
            var_to_set_name,
            source_value_argument,
        )

        expected_value = value_template.format(
            my_var=my_var.value,
            your_var=your_var.value,
        )

        environ__before = {
            my_var.name: my_var.value,
            your_var.name: your_var.value,
        }

        expected_environ__after = {
            var_to_set_name: expected_value,
            my_var.name: my_var.value,
            your_var.name: your_var.value,
        }

        # ACT & ASSERT #

        _CHECKER.check__w_source_variants(
            self,
            source,
            arrangement=
            ArrangementWithSds(
                process_execution_settings=
                execution_elements.with_environ_copy(environ__before),
            ),
            expectation=
            embryo_check.Expectation(
                main_side_effect_on_environment_variables=asrt.equals(expected_environ__after),
            )
        )

    def test_a_references_to_a_non_existing_env_var_SHOULD_be_replaced_with_empty_string(self):
        existing_var = NameAndValue('existing', 'EXISTING')
        non_existing_var__name = 'non_existing'
        new_var_to_set__name = 'new_var_to_set'

        source = syntax_for_set(
            new_var_to_set__name,
            env_var_ref_syntax(non_existing_var__name)
        )
        # ACT & ASSERT #

        _CHECKER.check__w_source_variants(
            self,
            source,
            embryo_check.ArrangementWithSds(
                process_execution_settings=
                proc_exe_env_for_test(
                    environ={
                        existing_var.name: existing_var.value
                    }
                )
            ),
            embryo_check.Expectation(
                main_result=asrt.is_none,
                main_side_effect_on_environment_variables=asrt.equals(
                    {
                        existing_var.name: existing_var.value,
                        new_var_to_set__name: '',
                    }
                )
            )
        )


class TestUnset(unittest.TestCase):
    def test_existing_variable(self):
        var_a = NameAndValue('a', 'A')
        var_b = NameAndValue('b', 'B')

        environ__before = NameAndValue.as_dict([var_a, var_b])
        environ__after = NameAndValue.as_dict([var_b])

        _CHECKER.check__w_source_variants(
            self,
            syntax_for_unset(var_a.name),
            ArrangementWithSds(
                process_execution_settings=
                execution_elements.with_environ_copy(environ__before),
            ),
            embryo_check.Expectation(
                main_side_effect_on_environment_variables=asrt.equals(environ__after),
            )
        )

    def test_WHEN_var_name_is_not_an_existing_env_var_THEN_env_SHOULD_be_unmodified(self):
        non_existing_var_name = 'non_existing'
        existing_var = NameAndValue('existing', 'EXISTING')

        environ__before = NameAndValue.as_dict([existing_var])
        environ__after = NameAndValue.as_dict([existing_var])

        _CHECKER.check__w_source_variants(
            self,
            syntax_for_unset(non_existing_var_name),
            ArrangementWithSds(
                process_execution_settings=
                execution_elements.with_environ_copy(environ__before),
            ),
            embryo_check.Expectation(
                main_side_effect_on_environment_variables=asrt.equals(environ__after),
            )
        )

    def test_argument_elements_on_multiple_lines(self):
        # ACT & ASSERT #
        var_name = 'ENV_VAR'

        sf = StringFormatter({
            'unset': sut.UNSET_IDENTIFIER,
            'name': var_name,
        })
        cases = [
            NameAndValue(
                'var name on following line',
                sf.format('{unset} \n{name}')
            ),
            NameAndValue(
                'token for unset on following line',
                sf.format('\n{unset} {name}')
            ),
            NameAndValue(
                'all elements on separate lines',
                sf.format('\n{unset} \n {name}')
            ),
        ]

        environ__before = {
            var_name: 'var_value'
        }
        environ__after = {}

        expectation = asrt.equals(environ__after)

        for case in cases:
            with self.subTest(case.name):
                # ACT & ASSERT #
                _CHECKER.check__w_source_variants(
                    self,
                    case.value,
                    embryo_check.ArrangementWithSds(
                        process_execution_settings=
                        proc_exe_env_for_test(
                            environ=environ__before
                        )
                    ),
                    embryo_check.Expectation(
                        main_result=asrt.is_none,
                        main_side_effect_on_environment_variables=expectation
                    )
                )


def syntax_for_set(name: str, value_expr: WithToString) -> str:
    return ' '.join([name, sut.ASSIGNMENT_IDENTIFIER, str(value_expr)])


def syntax_for_unset(name: str) -> str:
    return ' '.join([sut.UNSET_IDENTIFIER, name])


def syntax_for_set__nav(var: NameAndValue[WithToString]) -> str:
    return syntax_for_set(var.name, var.value)


def env_var_ref_syntax(var_name: str) -> Surrounded:
    return Surrounded('${', '}', var_name)


def dummy_resolving_env() -> PathResolvingEnvironmentPreOrPostSds:
    return PathResolvingEnvironmentPreOrPostSds(fake_tcds())


_CHECKER = embryo_check.Checker(sut.EmbryoParser())
