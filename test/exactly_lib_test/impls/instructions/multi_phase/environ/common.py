import unittest
from typing import Dict

from exactly_lib.impls.instructions.multi_phase.environ import defs, doc
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.parse.token import QuoteType
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings
from exactly_lib_test.common.help.test_resources.check_documentation import suite_for_instruction_documentation
from exactly_lib_test.impls.instructions.multi_phase.environ.test_resources.abstract_syntax import \
    SetVariableArgumentsAbsStx, UnsetVariableArgumentsAbsStx, env_var_ref_syntax
from exactly_lib_test.impls.instructions.multi_phase.environ.test_resources.instruction_check import CHECKER, \
    PARSE_CHECKER, PHASE_SPECS
from exactly_lib_test.impls.instructions.multi_phase.test_resources import \
    instruction_embryo_check as embryo_check
from exactly_lib_test.impls.types.string_source.test_resources import validation_cases as str_src_validation_cases
from exactly_lib_test.impls.types.string_source.test_resources.abstract_syntaxes import StringSourceOfStringAbsStx
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.test_resources.source.custom_abstract_syntax import SequenceAbsStx
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.types.string.test_resources.abstract_syntaxes import StringLiteralAbsStx, \
    MISSING_END_QUOTE__SOFT, MISSING_END_QUOTE_STR__HARD
from exactly_lib_test.type_val_deps.types.string.test_resources.string import StringConstantSymbolContext, \
    StringSymbolContext
from exactly_lib_test.util.process_execution.test_resources.proc_exe_env import proc_exe_env_for_test


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        suite_for_instruction_documentation(doc.TheInstructionDocumentation('instruction name')),
        TestInvalidSyntaxOfSetShouldBeDetected(),
        TestInvalidSyntaxOfUnsetShouldBeDetected(),
        TestSetValidationOfValue(),
        unittest.makeSuite(TestSet),
        unittest.makeSuite(TestSetWithReferencesToExistingEnvVars),
        unittest.makeSuite(TestUnset),
    ])


class TestInvalidSyntaxOfSetShouldBeDetected(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        for phase_spec in PHASE_SPECS:
            cases = [
                NameAndValue(
                    'missing arguments',
                    SetVariableArgumentsAbsStx(StringLiteralAbsStx(''),
                                               StringSourceOfStringAbsStx.of_str(''),
                                               phase_spec=phase_spec),
                ),
                NameAndValue(
                    'more than three arguments',
                    SetVariableArgumentsAbsStx(StringLiteralAbsStx('arg1'),
                                               StringSourceOfStringAbsStx.of_str('arg2 arg3'),
                                               phase_spec=phase_spec),
                ),
                NameAndValue(
                    'invalid quoting of value',
                    SetVariableArgumentsAbsStx(StringLiteralAbsStx('name'),
                                               StringSourceOfStringAbsStx(MISSING_END_QUOTE__SOFT),
                                               phase_spec=phase_spec),
                ),
            ]
            for case in cases:
                # ACT & ASSERT #
                PARSE_CHECKER.check_invalid_syntax__abs_stx(self, case.value,
                                                            phase_spec=phase_spec,
                                                            variant=case.name)


class TestInvalidSyntaxOfUnsetShouldBeDetected(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        for phase_spec in PHASE_SPECS:
            cases = [
                NameAndValue(
                    'invalid quoting',
                    UnsetVariableArgumentsAbsStx.of_str(MISSING_END_QUOTE_STR__HARD, phase_spec=phase_spec),
                ),
                NameAndValue(
                    'missing arguments',
                    UnsetVariableArgumentsAbsStx(StringLiteralAbsStx(''),
                                                 phase_spec=phase_spec),
                ),
                NameAndValue(
                    'more than one argument',
                    SequenceAbsStx.followed_by_superfluous(
                        UnsetVariableArgumentsAbsStx(StringLiteralAbsStx('name'),
                                                     phase_spec=phase_spec)
                    )
                ),
                NameAndValue(
                    'unset identifier must not be quoted',
                    SequenceAbsStx([
                        StringLiteralAbsStx(defs.UNSET_IDENTIFIER, QuoteType.HARD),
                        StringLiteralAbsStx('var_name'),
                    ])
                ),
            ]
            for case in cases:
                # ACT & ASSERT #
                PARSE_CHECKER.check_invalid_syntax__abs_stx(self, case.value,
                                                            phase_spec=phase_spec,
                                                            variant=case.name)


class TestSetValidationOfValue(unittest.TestCase):
    def runTest(self):
        # ACT & ASSERT #
        name = StringLiteralAbsStx('name')

        for phase_spec in PHASE_SPECS:
            for validation_case in str_src_validation_cases.failing_validation_cases():
                CHECKER.check__abs_stx__std_layouts_and_source_variants(
                    self,
                    SetVariableArgumentsAbsStx(name,
                                               validation_case.value.syntax,
                                               phase_spec=phase_spec),
                    embryo_check.Arrangement.setup_phase_aware(),
                    embryo_check.MultiSourceExpectation.setup_phase_aware(
                        validation=validation_case.value.assertion,
                    ),
                    phase_spec=phase_spec,
                    validation_case=validation_case.name,
                )


class TestSet(unittest.TestCase):
    def test_constant_string_value__current_is_not_none(self):
        # ACT & ASSERT #
        var = NameAndValue('name', 'value')

        CHECKER.check__abs_stx__std_layouts_and_source_variants(
            self,
            SetVariableArgumentsAbsStx.of_nav(var, phase_spec=None),
            embryo_check.Arrangement.setup_phase_aware(
                process_execution_settings=
                proc_exe_env_for_test(
                    environ={}
                )
            ),
            embryo_check.MultiSourceExpectation.setup_phase_aware(
                main_result=asrt.is_none,
                main_side_effect_on_environment_variables=asrt.equals(
                    {
                        var.name: var.value
                    }
                )
            )
        )

    def test_current_environ_is_none(self):
        # ACT & ASSERT #
        var_in_default = NameAndValue('var_in_default', 'value of var in default')

        def get_default_environ() -> Dict[str, str]:
            return NameAndValue.as_dict([var_in_default])

        var_to_set = NameAndValue('var_to_set', 'value')

        CHECKER.check__abs_stx__std_layouts_and_source_variants(
            self,
            SetVariableArgumentsAbsStx.of_nav(var_to_set, phase_spec=None),
            embryo_check.Arrangement.setup_phase_aware(
                process_execution_settings=
                proc_exe_env_for_test(environ=None),
                default_environ_getter=get_default_environ,
            ),
            embryo_check.MultiSourceExpectation.setup_phase_aware(
                main_result=asrt.is_none,
                main_side_effect_on_environment_variables=asrt.equals(
                    NameAndValue.as_dict([var_in_default, var_to_set])
                )
            )
        )

    def test_multi_line_value(self):
        # ARRANGE #
        var = NameAndValue('name', 'a\nmulti\nline\nvalue\n')
        environ__before = {}
        environ__after = {var.name: var.value}

        # ACT & ASSERT #
        CHECKER.check__abs_stx__std_layouts_and_source_variants(
            self,
            SetVariableArgumentsAbsStx.of_str(var.name, var.value,
                                              phase_spec=None,
                                              quoting=QuoteType.HARD),
            embryo_check.Arrangement.setup_phase_aware(
                process_execution_settings=
                proc_exe_env_for_test(
                    environ=environ__before
                )
            ),
            embryo_check.MultiSourceExpectation.setup_phase_aware(
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

        CHECKER.check__abs_stx__std_layouts_and_source_variants(
            self,
            SetVariableArgumentsAbsStx.of_str(var_name, value_after, phase_spec=None),
            embryo_check.Arrangement.setup_phase_aware(
                process_execution_settings=
                proc_exe_env_for_test(
                    environ=environ__before
                )
            ),
            embryo_check.MultiSourceExpectation.setup_phase_aware(
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

        source_syntax = SetVariableArgumentsAbsStx.of_str(variable_name,
                                                          value_source_string,
                                                          phase_spec=None,
                                                          quoting=QuoteType.SOFT)

        # ACT & ASSERT #

        CHECKER.check__abs_stx__std_layouts_and_source_variants(
            self,
            source_syntax,
            embryo_check.Arrangement.setup_phase_aware(
                symbols=
                SymbolContext.symbol_table_of_contexts([my_symbol, your_symbol]),
                process_execution_settings=
                ProcessExecutionSettings.with_environ({}),
            ),
            embryo_check.MultiSourceExpectation.setup_phase_aware(
                main_side_effect_on_environment_variables=asrt.equals(expected_environ_after_main),
                symbol_usages=asrt.matches_sequence([
                    my_symbol.usage_assertion__any_data_type,
                    your_symbol.usage_assertion__any_data_type,
                ]),
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

        source_syntax = SetVariableArgumentsAbsStx.of_str(variable_name,
                                                          value_source_string,
                                                          phase_spec=None,
                                                          quoting=QuoteType.HARD)

        # ACT & ASSERT #

        CHECKER.check__abs_stx__std_layouts_and_source_variants(
            self,
            source_syntax,
            embryo_check.Arrangement.setup_phase_aware(
                process_execution_settings=
                ProcessExecutionSettings.with_environ({}),
            ),
            embryo_check.MultiSourceExpectation.setup_phase_aware(
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

        CHECKER.check__abs_stx__std_layouts_and_source_variants(
            self,
            SetVariableArgumentsAbsStx.of_str(defined_env_var.name,
                                              env_var_ref_syntax(existing_env_var.name),
                                              phase_spec=None),
            arrangement=
            embryo_check.Arrangement.setup_phase_aware(
                process_execution_settings=
                ProcessExecutionSettings.with_environ(environ__before),
            ),
            expectation=
            embryo_check.MultiSourceExpectation.setup_phase_aware(
                main_side_effect_on_environment_variables=asrt.equals(environ__after),
            )
        )

    def test_set_value_that_references_an_env_var_in_string_ref_value(self):
        # ARRANGE #

        existing_env_var = NameAndValue('MY_VAR', 'MY_VAL')
        defined_env_var = NameAndValue('name', existing_env_var.value)

        string_symbol_w_env_var_ref = StringSymbolContext.of_constant(
            'SYMBOL_W_ENV_VAR_REF',
            env_var_ref_syntax(existing_env_var.name)
        )

        environ__before = {
            existing_env_var.name: existing_env_var.value,
        }
        environ__after = {
            defined_env_var.name: defined_env_var.value,
            existing_env_var.name: existing_env_var.value,
        }

        # ACT & ASSERT #

        CHECKER.check__abs_stx__std_layouts_and_source_variants(
            self,
            SetVariableArgumentsAbsStx(StringLiteralAbsStx(defined_env_var.name),
                                       StringSourceOfStringAbsStx(string_symbol_w_env_var_ref.abstract_syntax),
                                       phase_spec=None),
            arrangement=
            embryo_check.Arrangement.setup_phase_aware(
                symbols=string_symbol_w_env_var_ref.symbol_table,
                process_execution_settings=
                ProcessExecutionSettings.with_environ(environ__before),
            ),
            expectation=
            embryo_check.MultiSourceExpectation.setup_phase_aware(
                symbol_usages=asrt.matches_singleton_sequence(
                    string_symbol_w_env_var_ref.reference_assertion__convertible_to_string
                ),
                main_side_effect_on_environment_variables=asrt.equals(environ__after),
            )
        )

    def test_set_value_that_contains_text_and_references_to_env_vars(self):
        # ARRANGE #

        my_var = NameAndValue('MY_VAR', 'MY_VAL')
        your_var = NameAndValue('YOUR_VAR', 'YOUR_VAL')
        var_to_set_name = 'name'

        value_template = 'pre {my_var} {your_var} post'

        source = SetVariableArgumentsAbsStx.of_str(
            var_to_set_name,
            value_template.format(
                my_var=env_var_ref_syntax(my_var.name),
                your_var=env_var_ref_syntax(your_var.name),
            ),
            phase_spec=None,
            quoting=QuoteType.SOFT,
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

        CHECKER.check__abs_stx__std_layouts_and_source_variants(
            self,
            source,
            arrangement=
            embryo_check.Arrangement.setup_phase_aware(
                process_execution_settings=
                ProcessExecutionSettings.with_environ(environ__before),
            ),
            expectation=
            embryo_check.MultiSourceExpectation.setup_phase_aware(
                main_side_effect_on_environment_variables=asrt.equals(expected_environ__after),
            )
        )

    def test_a_references_to_a_non_existing_env_var_SHOULD_be_replaced_with_empty_string(self):
        # ARRANGE #
        existing_var = NameAndValue('existing', 'EXISTING')
        non_existing_var__name = 'non_existing'
        new_var_to_set__name = 'new_var_to_set'

        source = SetVariableArgumentsAbsStx.of_str(
            new_var_to_set__name,
            env_var_ref_syntax(non_existing_var__name),
            phase_spec=None,
        )
        # ACT & ASSERT #

        CHECKER.check__abs_stx__std_layouts_and_source_variants(
            self,
            source,
            embryo_check.Arrangement.setup_phase_aware(
                process_execution_settings=
                proc_exe_env_for_test(
                    environ={
                        existing_var.name: existing_var.value
                    }
                )
            ),
            embryo_check.MultiSourceExpectation.setup_phase_aware(
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

        CHECKER.check__abs_stx__std_layouts_and_source_variants(
            self,
            UnsetVariableArgumentsAbsStx.of_str(var_a.name, phase_spec=None),
            embryo_check.Arrangement.setup_phase_aware(
                process_execution_settings=
                ProcessExecutionSettings.with_environ(environ__before),
            ),
            embryo_check.MultiSourceExpectation.setup_phase_aware(
                main_side_effect_on_environment_variables=asrt.equals(environ__after),
            )
        )

    def test_current_environ_is_none(self):
        var_a = NameAndValue('a', 'A')
        var_b = NameAndValue('b', 'B')

        environ__before = NameAndValue.as_dict([var_a, var_b])
        environ__after = NameAndValue.as_dict([var_b])

        def get_default_environ() -> Dict[str, str]:
            return dict(environ__before)

        CHECKER.check__abs_stx__std_layouts_and_source_variants(
            self,
            UnsetVariableArgumentsAbsStx.of_str(var_a.name, phase_spec=None),
            embryo_check.Arrangement.setup_phase_aware(
                process_execution_settings=
                proc_exe_env_for_test(environ=None),
                default_environ_getter=get_default_environ,
            ),
            embryo_check.MultiSourceExpectation.setup_phase_aware(
                main_side_effect_on_environment_variables=asrt.equals(environ__after),
            )
        )

    def test_WHEN_var_name_is_not_an_existing_env_var_THEN_env_SHOULD_be_unmodified(self):
        non_existing_var_name = 'non_existing'
        existing_var = NameAndValue('existing', 'EXISTING')

        environ__before = NameAndValue.as_dict([existing_var])
        environ__after = NameAndValue.as_dict([existing_var])

        CHECKER.check__abs_stx__std_layouts_and_source_variants(
            self,
            UnsetVariableArgumentsAbsStx.of_str(non_existing_var_name, phase_spec=None),
            embryo_check.Arrangement.setup_phase_aware(
                process_execution_settings=
                ProcessExecutionSettings.with_environ(environ__before),
            ),
            embryo_check.MultiSourceExpectation.setup_phase_aware(
                main_side_effect_on_environment_variables=asrt.equals(environ__after),
            )
        )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
