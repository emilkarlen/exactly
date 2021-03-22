import unittest
from typing import Mapping, Optional, Callable, List, Sequence

from exactly_lib.impls.instructions.multi_phase.environ.impl import Phase
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.execution.test_resources.predefined_properties import get_empty_environ
from exactly_lib_test.impls.instructions.multi_phase.environ.test_resources.abstract_syntax import \
    SetVariableArgumentsAbsStx, UnsetVariableArgumentsAbsStx, env_var_ref_syntax
from exactly_lib_test.impls.instructions.multi_phase.environ.test_resources.environs_setup import EnvVar, \
    EnvironsSetupForSetBase, EnvironsSetupForUnsetBase, EnvVarDict, EnvironsSetup
from exactly_lib_test.impls.instructions.multi_phase.environ.test_resources.instruction_check import CHECKER
from exactly_lib_test.impls.instructions.multi_phase.environ.test_resources.referenses_setup import NameWSymRefs, \
    ValueWSymRefsAndVarRefs
from exactly_lib_test.impls.instructions.multi_phase.test_resources.embryo_arr_exp import SetupSettingsArr, Arrangement, \
    ExecutionExpectation
from exactly_lib_test.impls.types.string_source.test_resources.abstract_syntaxes import \
    StringSourceOfStringAbsStx
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.test_case.test_resources import instr_settings_assertions as asrt_instr_settings
from exactly_lib_test.test_case.test_resources import settings_builder_assertions as asrt_setup_settings
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
    def expectation_of_addition_to_phase_act(self,
                                             var_to_add: EnvVar,
                                             contents_of_non_checked_phase: Optional[Mapping[str, str]],
                                             ) -> ExecutionExpectation:
        return expectation(
            non_act=contents_of_non_checked_phase,
            the_act=self.with_added__as_dict(Phase.ACT, var_to_add),
        )

    def expectation_of_addition_to_phase_non_act(self,
                                                 var_to_add: EnvVar,
                                                 contents_of_non_checked_phase: Optional[Mapping[str, str]],
                                                 ) -> ExecutionExpectation[None]:
        return expectation(
            non_act=self.with_added__as_dict(Phase.NON_ACT, var_to_add),
            the_act=contents_of_non_checked_phase,
        )

    def expectation_of_addition_to_phase_all(self, var_to_add: EnvVar) -> ExecutionExpectation:
        return self.expectation_of_addition(var_to_add, var_to_add)

    def expectation_of_addition(self,
                                additional_in_act: EnvVar,
                                additional_in_non_act: EnvVar,
                                ) -> ExecutionExpectation:
        return expectation(
            non_act=self.with_added__as_dict(Phase.NON_ACT, additional_in_non_act),
            the_act=self.with_added__as_dict(Phase.ACT, additional_in_act),
        )


class EnvironsSetupForUnset(EnvironsSetupForUnsetBase):
    def expectation_of_removal_from_phase_act(self,
                                              var_to_remove: str,
                                              contents_of_non_checked_phase: Optional[Mapping[str, str]],
                                              ) -> ExecutionExpectation:
        return expectation(
            non_act=contents_of_non_checked_phase,
            the_act=self.with_removed__as_dict(Phase.ACT, var_to_remove),
        )

    def expectation_of_removal_from_phase_non_act(self,
                                                  var_to_remove: str,
                                                  contents_of_non_checked_phase: Optional[Mapping[str, str]],
                                                  ) -> ExecutionExpectation[None]:
        return expectation(
            non_act=self.with_removed__as_dict(Phase.NON_ACT, var_to_remove),
            the_act=contents_of_non_checked_phase,
        )

    def expectation_of_removal_from_phase_all(self, var_to_remove: str) -> ExecutionExpectation:
        return expectation(
            non_act=self.with_removed__as_dict(Phase.NON_ACT, var_to_remove),
            the_act=self.with_removed__as_dict(Phase.ACT, var_to_remove),
        )


ExeCasesForContentsOfOtherGetter = Callable[[Optional[Mapping[str, str]]],
                                            List[NArrEx[Arrangement, ExecutionExpectation[None]]]]


class TestSet(unittest.TestCase):
    VAR_TO_SET = NameAndValue('var_to_set', 'value_to_set')
    EXISTING_VAR = NameAndValue('existing_var', 'value of existing var')
    ENVIRONS_SETUP__IDENTICAL = EnvironsSetupForSet(
        the_act=[EXISTING_VAR],
        non_act=[EXISTING_VAR],
    )
    ENVIRONS_SETUP__DIFFERENT = EnvironsSetupForSet(
        the_act=[NameAndValue('act_1', ' value of act_1')],
        non_act=[NameAndValue('non_act_1', ' value of non_act_1')],
    )

    def test_target_is_non_act(self):
        # ACT & ASSERT #
        setup = self.ENVIRONS_SETUP__DIFFERENT
        var_to_set = self.VAR_TO_SET

        def execution_cases(contents_of_non_checked_phase: Optional[Mapping[str, str]]
                            ) -> List[NArrEx[Arrangement, ExecutionExpectation[None]]]:
            expectation_of_added_var = setup.expectation_of_addition_to_phase_non_act(
                var_to_set,
                contents_of_non_checked_phase=contents_of_non_checked_phase,
            )

            return [
                NArrEx(
                    'environ/existing (not None), other_is_populated={}'.format(
                        contents_of_non_checked_phase is not None
                    ),
                    arr(
                        non_act=setup.as_dict(Phase.NON_ACT),
                        the_act=contents_of_non_checked_phase,
                        defaults_getter=get_empty_environ,
                    ),
                    expectation_of_added_var,
                ),
                NArrEx(
                    'environ/non existing (None), other_is_populated={}'.format(
                        contents_of_non_checked_phase is not None
                    ),
                    arr(
                        non_act=None,
                        the_act=contents_of_non_checked_phase,
                        defaults_getter=setup.defaults_getter_with_values(Phase.NON_ACT),
                    ),
                    expectation_of_added_var,
                ),
            ]

        # ACT & ASSERT #
        self._check_modification_of_single_phase(
            Phase.NON_ACT,
            var_to_set,
            execution_cases,
            contents_of_non_checked_phase__populated=setup.as_dict(Phase.ACT),
        )

    def test_target_is_act(self):
        # ACT & ASSERT #
        setup = self.ENVIRONS_SETUP__DIFFERENT
        var_to_set = self.VAR_TO_SET

        def execution_cases(contents_of_non_checked_phase: Optional[Mapping[str, str]]
                            ) -> List[NArrEx[Arrangement, ExecutionExpectation[None]]]:
            expectation_of_added_var = setup.expectation_of_addition_to_phase_act(
                var_to_set,
                contents_of_non_checked_phase=contents_of_non_checked_phase,
            )

            return [
                NArrEx(
                    'environ/existing (not None), other_is_populated={}'.format(
                        contents_of_non_checked_phase is not None
                    ),
                    arr(
                        non_act=contents_of_non_checked_phase,
                        the_act=setup.as_dict(Phase.ACT),
                        defaults_getter=get_empty_environ,
                    ),
                    expectation_of_added_var,
                ),
                NArrEx(
                    'environ/non existing (None), other_is_populated={}'.format(
                        contents_of_non_checked_phase is not None
                    ),
                    arr(
                        non_act=contents_of_non_checked_phase,
                        the_act=None,
                        defaults_getter=setup.defaults_getter_with_values(Phase.ACT),
                    ),
                    expectation_of_added_var,
                ),
            ]

        # ACT & ASSERT #
        self._check_modification_of_single_phase(
            Phase.ACT,
            var_to_set,
            execution_cases,
            contents_of_non_checked_phase__populated=setup.as_dict(Phase.NON_ACT),
        )

    def test_target_is_all_phases(self):
        # ACT & ASSERT #
        setup = self.ENVIRONS_SETUP__DIFFERENT
        identical_setup = self.ENVIRONS_SETUP__IDENTICAL
        var_to_set = self.VAR_TO_SET

        arbitrary_phase = Phase.NON_ACT

        all_execution_cases = [
            NArrEx(
                'non-act/populated, act/populated',
                arr(
                    non_act=setup.as_dict(Phase.NON_ACT),
                    the_act=setup.as_dict(Phase.ACT),
                    defaults_getter=get_empty_environ,
                ),
                setup.expectation_of_addition_to_phase_all(var_to_set),
            ),
            NArrEx(
                'non-act/populated, act/not populated',
                arr(
                    non_act=setup.as_dict(Phase.NON_ACT),
                    the_act=None,
                    defaults_getter=setup.defaults_getter_with_values(Phase.ACT),
                ),
                setup.expectation_of_addition_to_phase_all(var_to_set),
            ),
            NArrEx(
                'non-act/not populated, act/populated',
                arr(
                    non_act=None,
                    the_act=setup.as_dict(Phase.ACT),
                    defaults_getter=setup.defaults_getter_with_values(Phase.NON_ACT),
                ),
                setup.expectation_of_addition_to_phase_all(var_to_set),
            ),
            NArrEx(
                'non-act/not populated, act/not populated',
                arr(
                    non_act=None,
                    the_act=None,
                    defaults_getter=identical_setup.defaults_getter_with_values(arbitrary_phase),
                ),
                identical_setup.expectation_of_addition_to_phase_all(var_to_set),
            ),
        ]
        # ACT & ASSERT #
        CHECKER.check__abs_stx__multi__std_layouts_and_source_variants(
            self,
            SetVariableArgumentsAbsStx.of_nav(var_to_set, phase_spec=None),
            symbol_usages=asrt.is_empty_sequence,
            execution_cases=all_execution_cases,
        )

    def _check_modification_of_single_phase(self,
                                            phase_to_modify: Phase,
                                            var_to_set: EnvVar,
                                            execution_cases: ExeCasesForContentsOfOtherGetter,
                                            contents_of_non_checked_phase__populated: EnvVarDict):
        # ARRANGE #
        all_execution_cases = (
                execution_cases(contents_of_non_checked_phase__populated) +
                execution_cases(None)
        )
        # ACT & ASSERT #
        CHECKER.check__abs_stx__multi__std_layouts_and_source_variants(
            self,
            SetVariableArgumentsAbsStx.of_nav(var_to_set, phase_spec=phase_to_modify),
            symbol_usages=asrt.is_empty_sequence,
            execution_cases=all_execution_cases,
        )


class TestSetWithReferencesToEnvVars(unittest.TestCase):
    def test_reference_should_be_resolved_in_manipulated_phase(self):
        common_var_name = 'existing_in_both_act_and_non_act'

        new_var_to_set = NameAndValue('name_of_var_to_set',
                                      env_var_ref_syntax(common_var_name))

        common_var_value = {
            Phase.NON_ACT: 'value of common var in non act',
            Phase.ACT: 'value of common var in act',
        }

        before_modification = EnvironsSetupForSet(
            non_act=[
                NameAndValue(common_var_name, common_var_value[Phase.NON_ACT]),
                NameAndValue('only_in_non_act', 'value of var only in non-act'),
            ],
            the_act=[
                NameAndValue(common_var_name, common_var_value[Phase.ACT]),
                NameAndValue('only_in_act', 'value of var only in act'),
            ],
        )
        after_modification = before_modification.new_with_added(
            non_act=NameAndValue(new_var_to_set.name, common_var_value[Phase.NON_ACT]),
            the_act=NameAndValue(new_var_to_set.name, common_var_value[Phase.ACT]),
        )
        all_execution_cases = _exe_cases_of_modification(before_modification, after_modification)
        # ACT & ASSERT #
        CHECKER.check__abs_stx__multi__std_layouts_and_source_variants(
            self,
            SetVariableArgumentsAbsStx.of_nav(new_var_to_set, phase_spec=None),
            symbol_usages=asrt.is_empty_sequence,
            execution_cases=all_execution_cases,
        )


class TestUnset(unittest.TestCase):
    COMMON_VAR_TO_UNSET = NameAndValue('common_var_to_unset', 'value of common var')
    EXISTING_VAR = NameAndValue('existing_var', 'value of existing var')
    ENVIRONS_SETUP__IDENTICAL = EnvironsSetupForUnset(
        the_act=[COMMON_VAR_TO_UNSET, EXISTING_VAR],
        non_act=[COMMON_VAR_TO_UNSET, EXISTING_VAR],
    )
    ENVIRONS_SETUP__DIFFERENT = EnvironsSetupForUnset(
        the_act=[NameAndValue('act_1', ' value of act_1'),
                 NameAndValue(COMMON_VAR_TO_UNSET.name, 'value of common in act')],
        non_act=[NameAndValue('non_act_1', ' value of non_act_1'),
                 NameAndValue(COMMON_VAR_TO_UNSET.name, 'value of common in non-act')],
    )

    def test_target_is_non_act(self):
        # ACT & ASSERT #
        setup = self.ENVIRONS_SETUP__DIFFERENT
        var_to_unset = self.COMMON_VAR_TO_UNSET.name

        def execution_cases(contents_of_non_checked_phase: Optional[Mapping[str, str]]
                            ) -> List[NArrEx[Arrangement, ExecutionExpectation[None]]]:
            expectation_of_removed_var = setup.expectation_of_removal_from_phase_non_act(
                var_to_unset,
                contents_of_non_checked_phase=contents_of_non_checked_phase,
            )

            return [
                NArrEx(
                    'environ/existing (not None), other_is_populated={}'.format(
                        contents_of_non_checked_phase is not None
                    ),
                    arr(
                        non_act=setup.as_dict(Phase.NON_ACT),
                        the_act=contents_of_non_checked_phase,
                        defaults_getter=get_empty_environ,
                    ),
                    expectation_of_removed_var,
                ),
                NArrEx(
                    'environ/non existing (None), other_is_populated={}'.format(
                        contents_of_non_checked_phase is not None
                    ),
                    arr(
                        non_act=None,
                        the_act=contents_of_non_checked_phase,
                        defaults_getter=setup.defaults_getter_with_values(Phase.NON_ACT),
                    ),
                    expectation_of_removed_var,
                ),
            ]

        # ACT & ASSERT #
        self._check_modification_of_single_phase(
            Phase.NON_ACT,
            var_to_unset,
            execution_cases,
            contents_of_non_checked_phase__populated=setup.as_dict(Phase.ACT),
        )

    def test_target_is_act(self):
        # ACT & ASSERT #
        setup = self.ENVIRONS_SETUP__DIFFERENT
        var_to_unset = self.COMMON_VAR_TO_UNSET.name

        def execution_cases(contents_of_non_checked_phase: Optional[Mapping[str, str]]
                            ) -> List[NArrEx[Arrangement, ExecutionExpectation[None]]]:
            expectation_of_removed_var = setup.expectation_of_removal_from_phase_act(
                var_to_unset,
                contents_of_non_checked_phase=contents_of_non_checked_phase,
            )

            return [
                NArrEx(
                    'environ/existing (not None), other_is_populated={}'.format(
                        contents_of_non_checked_phase is not None
                    ),
                    arr(
                        non_act=contents_of_non_checked_phase,
                        the_act=setup.as_dict(Phase.ACT),
                        defaults_getter=get_empty_environ,
                    ),
                    expectation_of_removed_var,
                ),
                NArrEx(
                    'environ/non existing (None), other_is_populated={}'.format(
                        contents_of_non_checked_phase is not None
                    ),
                    arr(
                        non_act=contents_of_non_checked_phase,
                        the_act=None,
                        defaults_getter=setup.defaults_getter_with_values(Phase.ACT),
                    ),
                    expectation_of_removed_var,
                ),
            ]

        # ACT & ASSERT #
        self._check_modification_of_single_phase(
            Phase.ACT,
            var_to_unset,
            execution_cases,
            contents_of_non_checked_phase__populated=setup.as_dict(Phase.NON_ACT),
        )

    def test_target_is_all_phases(self):
        # ACT & ASSERT #
        setup = self.ENVIRONS_SETUP__DIFFERENT
        identical_setup = self.ENVIRONS_SETUP__IDENTICAL
        var_to_unset = self.COMMON_VAR_TO_UNSET.name

        arbitrary_phase = Phase.NON_ACT

        all_execution_cases = [
            NArrEx(
                'non-act/populated, act/populated',
                arr(
                    non_act=setup.as_dict(Phase.NON_ACT),
                    the_act=setup.as_dict(Phase.ACT),
                    defaults_getter=get_empty_environ,
                ),
                setup.expectation_of_removal_from_phase_all(var_to_unset),
            ),
            NArrEx(
                'non-act/populated, act/not populated',
                arr(
                    non_act=setup.as_dict(Phase.NON_ACT),
                    the_act=None,
                    defaults_getter=setup.defaults_getter_with_values(Phase.ACT),
                ),
                setup.expectation_of_removal_from_phase_all(var_to_unset),
            ),
            NArrEx(
                'non-act/not populated, act/populated',
                arr(
                    non_act=None,
                    the_act=setup.as_dict(Phase.ACT),
                    defaults_getter=setup.defaults_getter_with_values(Phase.NON_ACT),
                ),
                setup.expectation_of_removal_from_phase_all(var_to_unset),
            ),
            NArrEx(
                'non-act/not populated, act/not populated',
                arr(
                    non_act=None,
                    the_act=None,
                    defaults_getter=identical_setup.defaults_getter_with_values(arbitrary_phase),
                ),
                identical_setup.expectation_of_removal_from_phase_all(var_to_unset),
            ),
        ]
        # ACT & ASSERT #
        CHECKER.check__abs_stx__multi__std_layouts_and_source_variants(
            self,
            UnsetVariableArgumentsAbsStx.of_str(var_to_unset, phase_spec=None),
            symbol_usages=asrt.is_empty_sequence,
            execution_cases=all_execution_cases,
        )

    def _check_modification_of_single_phase(self,
                                            phase_to_modify: Phase,
                                            var_to_unset: str,
                                            execution_cases: ExeCasesForContentsOfOtherGetter,
                                            contents_of_non_checked_phase__populated: EnvVarDict,
                                            ):
        # ARRANGE #
        all_execution_cases = (
                execution_cases(contents_of_non_checked_phase__populated) +
                execution_cases(None)
        )
        # ACT & ASSERT #
        CHECKER.check__abs_stx__multi__std_layouts_and_source_variants(
            self,
            UnsetVariableArgumentsAbsStx.of_str(var_to_unset, phase_spec=phase_to_modify),
            symbol_usages=asrt.is_empty_sequence,
            execution_cases=all_execution_cases,
        )


class TestSetWithSymbolAndVarReferences(unittest.TestCase):
    def runTest(self):
        vars_before = [ValueWSymRefsAndVarRefs.REFERENCED_VAR_1,
                       ValueWSymRefsAndVarRefs.REFERENCED_VAR_2]
        setup_before = EnvironsSetup(vars_before, vars_before)

        var_to_set__resolved = NameAndValue(NameWSymRefs.RESOLVED_STR,
                                            ValueWSymRefsAndVarRefs.VALUE_WO_VAR_REFS)

        all_symbols = NameWSymRefs.SYMBOL_CONTEXTS + ValueWSymRefsAndVarRefs.SYMBOL_CONTEXTS

        execution_cases = _exe_cases_of_modification(
            before_modification=setup_before,
            after_modification=setup_before.new_with_added(var_to_set__resolved,
                                                           var_to_set__resolved),
            symbols=SymbolContext.symbol_table_of_contexts(all_symbols),
        )
        # ACT & ASSERT #
        CHECKER.check__abs_stx__multi__std_layouts_and_source_variants(
            self,
            SetVariableArgumentsAbsStx(
                NameWSymRefs.STRING_ABS_STX,
                StringSourceOfStringAbsStx(ValueWSymRefsAndVarRefs.STRING_ABS_STX),
                phase_spec=None,
            ),
            symbol_usages=SymbolContext.usages_assertion_of_contexts(all_symbols),
            execution_cases=execution_cases,
        )


class TestUnsetWithSymbolReferences(unittest.TestCase):
    def runTest(self):
        var_to_unset = NameAndValue(NameWSymRefs.RESOLVED_STR, 'value of var')
        vars_before = EnvironsSetup([var_to_unset],
                                    [var_to_unset])

        all_symbols = NameWSymRefs.SYMBOL_CONTEXTS

        execution_cases = _exe_cases_of_modification(
            before_modification=vars_before,
            after_modification=vars_before.new_with_removed(var_to_unset.name),
            symbols=SymbolContext.symbol_table_of_contexts(all_symbols),
        )
        # ACT & ASSERT #
        CHECKER.check__abs_stx__multi__std_layouts_and_source_variants(
            self,
            UnsetVariableArgumentsAbsStx(NameWSymRefs.STRING_ABS_STX,
                                         phase_spec=None),
            symbol_usages=SymbolContext.usages_assertion_of_contexts(all_symbols),
            execution_cases=execution_cases,
        )


def arr(non_act: Optional[Mapping[str, str]],
        the_act: Optional[Mapping[str, str]],
        defaults_getter: Callable[[], EnvVarDict],
        symbols: Optional[SymbolTable] = None,
        ) -> Arrangement:
    return Arrangement.setup_phase_aware(
        symbols=symbols,
        process_execution_settings=
        proc_exe_env_for_test(
            environ=non_act,
        ),
        setup_settings=SetupSettingsArr(
            environ=the_act,
        ),
        default_environ_getter=defaults_getter,
    )


def expectation(non_act: Optional[Mapping[str, str]],
                the_act: Optional[Mapping[str, str]]) -> ExecutionExpectation[None]:
    return ExecutionExpectation.setup_phase_aware(
        main_result=asrt.is_none,
        instruction_settings=asrt_instr_settings.matches(
            environ=asrt.equals(non_act),
        ),
        setup_settings=asrt_setup_settings.matches(
            environ=asrt.equals(the_act)
        )
    )


def _exe_cases_of_modification(before_modification: EnvironsSetup,
                               after_modification: EnvironsSetup,
                               symbols: Optional[SymbolTable] = None,
                               ) -> Sequence[NArrEx[Arrangement, ExecutionExpectation[None]]]:
    expectation_after_manipulation = expectation(
        non_act=after_modification.as_dict(Phase.NON_ACT),
        the_act=after_modification.as_dict(Phase.ACT),
    )
    return [
        NArrEx(
            'non-act/populated, act/populated',
            arr(
                non_act=before_modification.as_dict(Phase.NON_ACT),
                the_act=before_modification.as_dict(Phase.ACT),
                defaults_getter=get_empty_environ,
                symbols=symbols,
            ),
            expectation_after_manipulation,
        ),
        NArrEx(
            'non-act/populated, act/not populated',
            arr(
                non_act=before_modification.as_dict(Phase.NON_ACT),
                the_act=None,
                defaults_getter=before_modification.defaults_getter_with_values(Phase.ACT),
                symbols=symbols,
            ),
            expectation_after_manipulation,
        ),
        NArrEx(
            'non-act/not populated, act/populated',
            arr(
                non_act=None,
                the_act=before_modification.as_dict(Phase.ACT),
                defaults_getter=before_modification.defaults_getter_with_values(Phase.NON_ACT),
                symbols=symbols,
            ),
            expectation_after_manipulation,
        ),
    ]


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
