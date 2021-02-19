import unittest
from typing import Sequence, Callable, Optional, Mapping

from exactly_lib.impls.instructions.multi_phase.environ.impl import Phase
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.execution.test_resources.predefined_properties import get_empty_environ
from exactly_lib_test.impls.instructions.multi_phase.environ.test_resources.abstract_syntax import \
    SetVariableArgumentsAbsStx, UnsetVariableArgumentsAbsStx, env_var_ref_syntax
from exactly_lib_test.impls.instructions.multi_phase.environ.test_resources.environs_setup import EnvVar, \
    EnvironsSetupForSetBase, EnvironsSetupForUnsetBase, EnvVarDict, EnvironsSetup, defaults_getter__of_nav
from exactly_lib_test.impls.instructions.multi_phase.environ.test_resources.instruction_check import CHECKER
from exactly_lib_test.impls.instructions.multi_phase.environ.test_resources.referenses_setup import \
    ValueWSymRefsAndVarRefs, NameWSymRefs
from exactly_lib_test.impls.instructions.multi_phase.test_resources.embryo_arr_exp import Arrangement, \
    ExecutionExpectation
from exactly_lib_test.impls.types.string_source.test_resources.abstract_syntaxes import StringSourceOfStringAbsStx
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.test_case.test_resources import instr_settings_assertions as asrt_instr_settings
from exactly_lib_test.test_resources.test_utils import NArrEx
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.process_execution.test_resources.proc_exe_env import proc_exe_env_for_test


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestSet),
        unittest.makeSuite(TestSetWithReferencesToEnvVars),
        TestSetWithSymbolAndVarReferences(),
        unittest.makeSuite(TestUnset),
        TestUnsetWithSymbolReferences(),
    ])


class EnvironsSetupForSet(EnvironsSetupForSetBase):
    def expectation_of_addition_to_phase(self, phase: Phase, var_to_add: EnvVar) -> ExecutionExpectation:
        return ExecutionExpectation.setup_phase_aware(
            main_result=asrt.is_none,
            instruction_settings=asrt_instr_settings.matches(
                environ=asrt.equals(self.with_added__as_dict(phase, var_to_add))
            )
        )


class EnvironsSetupForUnset(EnvironsSetupForUnsetBase):
    def expectation_of_removal_from_phase(self, phase: Phase, var_to_remove: str) -> ExecutionExpectation:
        return ExecutionExpectation.setup_phase_aware(
            main_result=asrt.is_none,
            instruction_settings=asrt_instr_settings.matches(
                environ=asrt.equals(self.with_removed__as_dict(phase, var_to_remove))
            )
        )


class TestSet(unittest.TestCase):
    def test_target_is_all_phases_or_non_act(self):
        # ACT & ASSERT #
        phase_spec__to_check_for_modifications = Phase.NON_ACT
        environs_setup = EnvironsSetupForSet(
            the_act=[NameAndValue('act_1', ' value of act_1')],
            non_act=[NameAndValue('non_act_1', ' value of non_act_1')],
        )
        for phase_spec__source in [None, Phase.NON_ACT]:
            var_to_set = NameAndValue('var_to_set', 'value_to_set')
            # ACT & ASSERT #
            CHECKER.check__abs_stx__multi__std_layouts_and_source_variants(
                self,
                SetVariableArgumentsAbsStx.of_nav(var_to_set,
                                                  phase_spec=phase_spec__source),
                symbol_usages=asrt.is_empty_sequence,
                execution_cases=[
                    NArrEx(
                        arr_.name,
                        arr_.value,
                        environs_setup.expectation_of_addition_to_phase(phase_spec__to_check_for_modifications,
                                                                        var_to_set),
                    )
                    for arr_ in _arr_for(environs_setup,
                                         phase_spec__to_check_for_modifications)
                ],
                phase_spec__source=phase_spec__source,
            )

    def test_target_is_act(self):
        # ACT & ASSERT #
        phase_spec__source = Phase.ACT
        phase_spec__to_check_for_modifications = Phase.NON_ACT
        environs_setup = EnvironsSetupForSet(
            the_act=[NameAndValue('act_1', ' value of act_1')],
            non_act=[NameAndValue('non_act_1', ' value of non_act_1')],
        )

        var_to_set = NameAndValue('var_to_set', 'value_to_set')
        # ACT & ASSERT #
        CHECKER.check__abs_stx__multi__std_layouts_and_source_variants(
            self,
            SetVariableArgumentsAbsStx.of_nav(var_to_set,
                                              phase_spec=phase_spec__source),
            symbol_usages=asrt.is_empty_sequence,
            execution_cases=_exe_cases_for_unmodified(environs_setup,
                                                      phase_spec__to_check_for_modifications),
        )


class TestSetWithReferencesToEnvVars(unittest.TestCase):
    def test_reference_should_be_resolved_in_the_manipulated_phase(self):
        existing_var = NameAndValue('existing_name', 'value of existing')
        new_var_to_set_w_ref = NameAndValue('name_of_var_to_set',
                                            env_var_ref_syntax(existing_var.name))

        vars_before = [existing_var]
        execution_cases = _exe_cases_of_modification(
            before_modification=vars_before,
            after_modification=[
                existing_var,
                NameAndValue(new_var_to_set_w_ref.name, existing_var.value)
            ]
        )
        # ACT & ASSERT #
        for phase_spec__source in [None, Phase.NON_ACT]:
            CHECKER.check__abs_stx__multi__std_layouts_and_source_variants(
                self,
                SetVariableArgumentsAbsStx.of_nav(new_var_to_set_w_ref,
                                                  phase_spec=phase_spec__source),
                symbol_usages=asrt.is_empty_sequence,
                execution_cases=execution_cases,
                phase_spec__source=phase_spec__source,
            )


class TestSetWithSymbolAndVarReferences(unittest.TestCase):
    def runTest(self):
        vars_before = [ValueWSymRefsAndVarRefs.REFERENCED_VAR_1,
                       ValueWSymRefsAndVarRefs.REFERENCED_VAR_2]
        var_to_set__resolved = NameAndValue(NameWSymRefs.RESOLVED_STR,
                                            ValueWSymRefsAndVarRefs.VALUE_WO_VAR_REFS)

        all_symbols = NameWSymRefs.SYMBOL_CONTEXTS + ValueWSymRefsAndVarRefs.SYMBOL_CONTEXTS

        execution_cases = _exe_cases_of_modification(
            before_modification=vars_before,
            after_modification=vars_before + [var_to_set__resolved],
            symbols=SymbolContext.symbol_table_of_contexts(all_symbols),
        )
        # ACT & ASSERT #
        for phase_spec__source in [None, Phase.NON_ACT]:
            CHECKER.check__abs_stx__multi__std_layouts_and_source_variants(
                self,
                SetVariableArgumentsAbsStx(NameWSymRefs.STRING_ABS_STX,
                                           StringSourceOfStringAbsStx(ValueWSymRefsAndVarRefs.STRING_ABS_STX),
                                           phase_spec=phase_spec__source),
                symbol_usages=SymbolContext.usages_assertion_of_contexts(all_symbols),
                execution_cases=execution_cases,
                phase_spec__source=phase_spec__source,
            )


class TestUnset(unittest.TestCase):
    def test_target_is_all_phases_or_non_act(self):
        # ACT & ASSERT #
        phase_spec__to_check_for_modifications = Phase.NON_ACT
        var_in_target = NameAndValue('non_act_1', ' value of non_act_1')
        environs_setup = EnvironsSetupForUnset(
            the_act=[NameAndValue('act_1', ' value of act_1')],
            non_act=[var_in_target],
        )
        for phase_spec__source in [None, Phase.NON_ACT]:
            # ACT & ASSERT #
            CHECKER.check__abs_stx__multi__std_layouts_and_source_variants(
                self,
                UnsetVariableArgumentsAbsStx.of_str(var_in_target.name,
                                                    phase_spec=phase_spec__source),
                symbol_usages=asrt.is_empty_sequence,
                execution_cases=[
                    NArrEx(
                        arr.name,
                        arr.value,
                        environs_setup.expectation_of_removal_from_phase(phase_spec__to_check_for_modifications,
                                                                         var_in_target.name),
                    )
                    for arr in _arr_for(environs_setup,
                                        phase_spec__to_check_for_modifications)
                ],
                phase_spec__source=phase_spec__source,
            )

    def test_target_is_act(self):
        # ACT & ASSERT #
        phase_spec__source = Phase.ACT
        phase_spec__to_check_for_modifications = Phase.NON_ACT
        var_in_target = NameAndValue('non_act_1', ' value of non_act_1')
        environs_setup = EnvironsSetupForUnset(
            the_act=[NameAndValue('act_1', ' value of act_1')],
            non_act=[var_in_target],
        )
        # ACT & ASSERT #
        CHECKER.check__abs_stx__multi__std_layouts_and_source_variants(
            self,
            UnsetVariableArgumentsAbsStx.of_str(var_in_target.name, phase_spec=phase_spec__source),
            symbol_usages=asrt.is_empty_sequence,
            execution_cases=_exe_cases_for_unmodified(environs_setup,
                                                      phase_spec__to_check_for_modifications),
        )


class TestUnsetWithSymbolReferences(unittest.TestCase):
    def runTest(self):
        vars_before = [NameAndValue(NameWSymRefs.RESOLVED_STR, 'value of var')]
        vars_after = []

        all_symbols = NameWSymRefs.SYMBOL_CONTEXTS

        execution_cases = _exe_cases_of_modification(
            before_modification=vars_before,
            after_modification=vars_after,
            symbols=SymbolContext.symbol_table_of_contexts(all_symbols),
        )
        # ACT & ASSERT #
        for phase_spec__source in [None, Phase.NON_ACT]:
            CHECKER.check__abs_stx__multi__std_layouts_and_source_variants(
                self,
                UnsetVariableArgumentsAbsStx(NameWSymRefs.STRING_ABS_STX,
                                             phase_spec=phase_spec__source),
                symbol_usages=SymbolContext.usages_assertion_of_contexts(all_symbols),
                execution_cases=execution_cases,
                phase_spec__source=phase_spec__source,
            )


def _arr_for(setup: EnvironsSetup, phase: Phase) -> Sequence[NameAndValue[Arrangement]]:
    def get_environ_of_modified_before_action() -> EnvVarDict:
        return setup.as_dict(phase)

    return [
        NameAndValue(
            'environ/existing (not None)',
            arr(setup.as_dict(phase),
                get_empty_environ,
                ),
        ),
        NameAndValue(
            'environ/non-existing (== None)',
            arr(None,
                get_environ_of_modified_before_action,
                ),
        ),
    ]


def arr(values: Optional[Mapping[str, str]],
        default_environ_getter: Callable[[], EnvVarDict],
        symbols: Optional[SymbolTable] = None,
        ) -> Arrangement:
    return Arrangement.setup_phase_aware(
        symbols=symbols,
        process_execution_settings=
        proc_exe_env_for_test(
            environ=values,
        ),
        default_environ_getter=default_environ_getter,
        setup_settings=None,
    )


def expectation(expected: Optional[Mapping[str, str]]) -> ExecutionExpectation[None]:
    return ExecutionExpectation.setup_phase_aware(
        main_result=asrt.is_none,
        instruction_settings=asrt_instr_settings.matches(
            environ=asrt.equals(expected),
        )
    )


def _exe_cases_for_unmodified(setup: EnvironsSetup,
                              phase: Phase,
                              ) -> Sequence[NArrEx[Arrangement, ExecutionExpectation[None]]]:
    return [
        NArrEx(
            'environ/existing (not None)',
            arr(setup.as_dict(phase),
                default_environ_getter=get_empty_environ,
                ),
            expectation(setup.as_dict(phase)),
        ),
        NArrEx(
            'environ/non-existing None)',
            arr(None,
                default_environ_getter=setup.defaults_getter_with_values(phase),
                ),
            expectation(None),
        ),
    ]


def _exe_cases_of_modification(before_modification: Sequence[NameAndValue[str]],
                               after_modification: Sequence[NameAndValue[str]],
                               symbols: Optional[SymbolTable] = None,
                               ) -> Sequence[NArrEx[Arrangement, ExecutionExpectation[None]]]:
    expected = expectation(NameAndValue.as_dict(after_modification))
    return [
        NArrEx(
            'environ/existing (not None)',
            arr(NameAndValue.as_dict(before_modification),
                default_environ_getter=get_empty_environ,
                symbols=symbols,
                ),
            expected,
        ),
        NArrEx(
            'environ/non-existing None)',
            arr(None,
                default_environ_getter=defaults_getter__of_nav(before_modification),
                symbols=symbols,
                ),
            expected,
        ),
    ]


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
