import unittest
from typing import Mapping, Optional, Callable, List

from exactly_lib.impls.instructions.multi_phase.environ.impl import Phase
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.execution.test_resources.predefined_properties import get_empty_environ
from exactly_lib_test.impls.instructions.multi_phase.environ.test_resources.abstract_syntax import \
    SetVariableArgumentsAbsStx, UnsetVariableArgumentsAbsStx
from exactly_lib_test.impls.instructions.multi_phase.environ.test_resources.environs_setup import EnvVar, \
    EnvironsSetupForSetBase, EnvironsSetupForUnsetBase, EnvVarDict
from exactly_lib_test.impls.instructions.multi_phase.environ.test_resources.instruction_check import CHECKER
from exactly_lib_test.impls.instructions.multi_phase.test_resources import \
    instruction_embryo_check as embryo_check
from exactly_lib_test.impls.instructions.multi_phase.test_resources.instruction_embryo_check import \
    ExecutionExpectation, SetupSettingsArr, Arrangement
from exactly_lib_test.test_case.test_resources import instr_settings_assertions as asrt_instr_settings
from exactly_lib_test.test_case.test_resources import settings_builder_assertions as asrt_setup_settings
from exactly_lib_test.test_resources.test_utils import NArrEx
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.process_execution.test_resources.proc_exe_env import proc_exe_env_for_test


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestSet),
        unittest.makeSuite(TestUnset),
    ])


class EnvironsSetupForSet(EnvironsSetupForSetBase):
    def expectation_of_addition_to_phase_act(self,
                                             var_to_add: EnvVar,
                                             contents_of_non_checked_phase: Optional[Mapping[str, str]],
                                             ) -> ExecutionExpectation:
        return expectation(
            non_act=contents_of_non_checked_phase,
            act=self.with_added__as_dict(Phase.ACT, var_to_add),
        )

    def expectation_of_addition_to_phase_non_act(self,
                                                 var_to_add: EnvVar,
                                                 contents_of_non_checked_phase: Optional[Mapping[str, str]],
                                                 ) -> ExecutionExpectation[None]:
        return expectation(
            non_act=self.with_added__as_dict(Phase.NON_ACT, var_to_add),
            act=contents_of_non_checked_phase,
        )

    def expectation_of_addition_to_phase_all(self, var_to_add: EnvVar) -> ExecutionExpectation:
        return expectation(
            non_act=self.with_added__as_dict(Phase.NON_ACT, var_to_add),
            act=self.with_added__as_dict(Phase.ACT, var_to_add),
        )


class EnvironsSetupForUnset(EnvironsSetupForUnsetBase):
    def expectation_of_removal_from_phase_act(self,
                                              var_to_remove: str,
                                              contents_of_non_checked_phase: Optional[Mapping[str, str]],
                                              ) -> ExecutionExpectation:
        return expectation(
            non_act=contents_of_non_checked_phase,
            act=self.with_removed__as_dict(Phase.ACT, var_to_remove),
        )

    def expectation_of_removal_from_phase_non_act(self,
                                                  var_to_remove: str,
                                                  contents_of_non_checked_phase: Optional[Mapping[str, str]],
                                                  ) -> ExecutionExpectation[None]:
        return expectation(
            non_act=self.with_removed__as_dict(Phase.NON_ACT, var_to_remove),
            act=contents_of_non_checked_phase,
        )

    def expectation_of_removal_from_phase_all(self, var_to_remove: str) -> ExecutionExpectation:
        return expectation(
            non_act=self.with_removed__as_dict(Phase.NON_ACT, var_to_remove),
            act=self.with_removed__as_dict(Phase.ACT, var_to_remove),
        )


ExeCasesForContentsOfOtherGetter = Callable[[Optional[Mapping[str, str]]],
                                            List[NArrEx[Arrangement, ExecutionExpectation[None]]]]


class TestSet(unittest.TestCase):
    VAR_TO_SET = NameAndValue('var_to_set', 'value_to_set')
    EXISTING_VAR = NameAndValue('existing_var', 'value of existing var')
    ENVIRONS_SETUP__IDENTICAL = EnvironsSetupForSet(
        act=[EXISTING_VAR],
        non_act=[EXISTING_VAR],
    )
    ENVIRONS_SETUP__DIFFERENT = EnvironsSetupForSet(
        act=[NameAndValue('act_1', ' value of act_1')],
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
                        act=contents_of_non_checked_phase,
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
                        act=contents_of_non_checked_phase,
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
                        act=setup.as_dict(Phase.ACT),
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
                        act=None,
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
                    act=setup.as_dict(Phase.ACT),
                    defaults_getter=get_empty_environ,
                ),
                setup.expectation_of_addition_to_phase_all(var_to_set),
            ),
            NArrEx(
                'non-act/populated, act/not populated',
                arr(
                    non_act=setup.as_dict(Phase.NON_ACT),
                    act=None,
                    defaults_getter=setup.defaults_getter_with_values(Phase.ACT),
                ),
                setup.expectation_of_addition_to_phase_all(var_to_set),
            ),
            NArrEx(
                'non-act/not populated, act/populated',
                arr(
                    non_act=None,
                    act=setup.as_dict(Phase.ACT),
                    defaults_getter=setup.defaults_getter_with_values(Phase.NON_ACT),
                ),
                setup.expectation_of_addition_to_phase_all(var_to_set),
            ),
            NArrEx(
                'non-act/not populated, act/not populated',
                arr(
                    non_act=None,
                    act=None,
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


class TestUnset(unittest.TestCase):
    COMMON_VAR_TO_UNSET = NameAndValue('common_var_to_unset', 'value of common var')
    EXISTING_VAR = NameAndValue('existing_var', 'value of existing var')
    ENVIRONS_SETUP__IDENTICAL = EnvironsSetupForUnset(
        act=[COMMON_VAR_TO_UNSET, EXISTING_VAR],
        non_act=[COMMON_VAR_TO_UNSET, EXISTING_VAR],
    )
    ENVIRONS_SETUP__DIFFERENT = EnvironsSetupForUnset(
        act=[NameAndValue('act_1', ' value of act_1'),
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
                        act=contents_of_non_checked_phase,
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
                        act=contents_of_non_checked_phase,
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
                        act=setup.as_dict(Phase.ACT),
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
                        act=None,
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
                    act=setup.as_dict(Phase.ACT),
                    defaults_getter=get_empty_environ,
                ),
                setup.expectation_of_removal_from_phase_all(var_to_unset),
            ),
            NArrEx(
                'non-act/populated, act/not populated',
                arr(
                    non_act=setup.as_dict(Phase.NON_ACT),
                    act=None,
                    defaults_getter=setup.defaults_getter_with_values(Phase.ACT),
                ),
                setup.expectation_of_removal_from_phase_all(var_to_unset),
            ),
            NArrEx(
                'non-act/not populated, act/populated',
                arr(
                    non_act=None,
                    act=setup.as_dict(Phase.ACT),
                    defaults_getter=setup.defaults_getter_with_values(Phase.NON_ACT),
                ),
                setup.expectation_of_removal_from_phase_all(var_to_unset),
            ),
            NArrEx(
                'non-act/not populated, act/not populated',
                arr(
                    non_act=None,
                    act=None,
                    defaults_getter=identical_setup.defaults_getter_with_values(arbitrary_phase),
                ),
                identical_setup.expectation_of_removal_from_phase_all(var_to_unset),
            ),
        ]
        # ACT & ASSERT #
        CHECKER.check__abs_stx__multi__std_layouts_and_source_variants(
            self,
            UnsetVariableArgumentsAbsStx(var_to_unset, phase_spec=None),
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
            UnsetVariableArgumentsAbsStx(var_to_unset, phase_spec=phase_to_modify),
            symbol_usages=asrt.is_empty_sequence,
            execution_cases=all_execution_cases,
        )


def arr(non_act: Optional[Mapping[str, str]],
        act: Optional[Mapping[str, str]],
        defaults_getter: Callable[[], EnvVarDict]) -> embryo_check.Arrangement:
    return embryo_check.Arrangement.setup_phase_aware(
        process_execution_settings=
        proc_exe_env_for_test(
            environ=non_act,
        ),
        setup_settings=SetupSettingsArr(
            environ=act,
        ),
        default_environ_getter=defaults_getter,
    )


def expectation(non_act: Optional[Mapping[str, str]],
                act: Optional[Mapping[str, str]]) -> ExecutionExpectation[None]:
    return embryo_check.ExecutionExpectation.setup_phase_aware(
        main_result=asrt.is_none,
        instruction_settings=asrt_instr_settings.matches(
            environ=asrt.equals(non_act),
        ),
        setup_settings=asrt_setup_settings.matches(
            environ=asrt.equals(act)
        )
    )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
