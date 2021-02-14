import unittest
from typing import Sequence

from exactly_lib.impls.instructions.multi_phase.environ.impl import Phase
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.execution.test_resources.predefined_properties import get_empty_environ
from exactly_lib_test.impls.instructions.multi_phase.environ.test_resources.abstract_syntax import \
    SetVariableArgumentsAbsStx, UnsetVariableArgumentsAbsStx
from exactly_lib_test.impls.instructions.multi_phase.environ.test_resources.environs_setup import EnvVar, \
    EnvironsSetupForSetBase, EnvironsSetupForUnsetBase, EnvVarDict, EnvironsSetup
from exactly_lib_test.impls.instructions.multi_phase.environ.test_resources.instruction_check import CHECKER
from exactly_lib_test.impls.instructions.multi_phase.test_resources import \
    instruction_embryo_check as embryo_check
from exactly_lib_test.impls.instructions.multi_phase.test_resources.instruction_embryo_check import \
    ExecutionExpectation, Arrangement
from exactly_lib_test.test_case.test_resources import instr_settings_assertions as asrt_instr_settings
from exactly_lib_test.test_resources.test_utils import NArrEx
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.process_execution.test_resources.proc_exe_env import proc_exe_env_for_test


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestSet),
        unittest.makeSuite(TestUnset),
    ])


class EnvironsSetupForSet(EnvironsSetupForSetBase):
    def expectation_of_addition_to_phase(self, phase: Phase, var_to_add: EnvVar) -> ExecutionExpectation:
        return embryo_check.ExecutionExpectation.setup_phase_aware(
            main_result=asrt.is_none,
            instruction_settings=asrt_instr_settings.matches(
                environ=asrt.equals(self.with_added__as_dict(phase, var_to_add))
            )
        )


class EnvironsSetupForUnset(EnvironsSetupForUnsetBase):
    def expectation_of_removal_from_phase(self, phase: Phase, var_to_remove: str) -> ExecutionExpectation:
        return embryo_check.ExecutionExpectation.setup_phase_aware(
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
            act=[NameAndValue('act_1', ' value of act_1')],
            non_act=[NameAndValue('non_act_1', ' value of non_act_1')],
        )
        for phase_spec__source in [None, Phase.NON_ACT]:
            var_to_set = NameAndValue('var_to_set', 'value_to_set')
            # ACT & ASSERT #
            CHECKER.check__abs_stx__multi__std_layouts_and_source_variants(
                self,
                SetVariableArgumentsAbsStx.of_nav(var_to_set, phase_spec=phase_spec__source),
                symbol_usages=asrt.is_empty_sequence,
                execution_cases=[
                    NArrEx(
                        arr.name,
                        arr.value,
                        environs_setup.expectation_of_addition_to_phase(phase_spec__to_check_for_modifications,
                                                                        var_to_set),
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
        environs_setup = EnvironsSetupForSet(
            act=[NameAndValue('act_1', ' value of act_1')],
            non_act=[NameAndValue('non_act_1', ' value of non_act_1')],
        )

        var_to_set = NameAndValue('var_to_set', 'value_to_set')
        # ACT & ASSERT #
        CHECKER.check__abs_stx__multi__std_layouts_and_source_variants(
            self,
            SetVariableArgumentsAbsStx.of_nav(var_to_set, phase_spec=phase_spec__source),
            symbol_usages=asrt.is_empty_sequence,
            execution_cases=_arr_exp_for_unmodified(environs_setup,
                                                    phase_spec__to_check_for_modifications),
        )


class TestUnset(unittest.TestCase):
    def test_target_is_all_phases_or_non_act(self):
        # ACT & ASSERT #
        phase_spec__to_check_for_modifications = Phase.NON_ACT
        var_in_target = NameAndValue('non_act_1', ' value of non_act_1')
        environs_setup = EnvironsSetupForUnset(
            act=[NameAndValue('act_1', ' value of act_1')],
            non_act=[var_in_target],
        )
        for phase_spec__source in [None, Phase.NON_ACT]:
            # ACT & ASSERT #
            CHECKER.check__abs_stx__multi__std_layouts_and_source_variants(
                self,
                UnsetVariableArgumentsAbsStx(var_in_target.name, phase_spec=phase_spec__source),
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
            act=[NameAndValue('act_1', ' value of act_1')],
            non_act=[var_in_target],
        )
        # ACT & ASSERT #
        CHECKER.check__abs_stx__multi__std_layouts_and_source_variants(
            self,
            UnsetVariableArgumentsAbsStx(var_in_target.name, phase_spec=phase_spec__source),
            symbol_usages=asrt.is_empty_sequence,
            execution_cases=_arr_exp_for_unmodified(environs_setup,
                                                    phase_spec__to_check_for_modifications),
        )


def _arr_for(setup: EnvironsSetup, phase: Phase) -> Sequence[NameAndValue[embryo_check.Arrangement]]:
    def get_environ_of_modified_before_action() -> EnvVarDict:
        return setup.as_dict(phase)

    return [
        NameAndValue(
            'environ/existing (not None)',
            embryo_check.Arrangement.setup_phase_aware(
                process_execution_settings=
                proc_exe_env_for_test(
                    environ=setup.as_dict(phase),
                ),
                default_environ_getter=get_empty_environ,
                setup_settings=None,
            )
        ),
        NameAndValue(
            'environ/non-existing (== None)',
            embryo_check.Arrangement.setup_phase_aware(
                process_execution_settings=
                proc_exe_env_for_test(
                    environ=None,
                ),
                default_environ_getter=get_environ_of_modified_before_action,
                setup_settings=None,
            )
        ),
    ]


def _arr_exp_for_unmodified(setup: EnvironsSetup, phase: Phase,
                            ) -> Sequence[NArrEx[Arrangement, ExecutionExpectation[None]]]:
    def get_environ_of_modified_before_action() -> EnvVarDict:
        return setup.as_dict(phase)

    return [
        NArrEx(
            'environ/existing (not None)',
            embryo_check.Arrangement.setup_phase_aware(
                process_execution_settings=
                proc_exe_env_for_test(
                    environ=setup.as_dict(phase),
                ),
                default_environ_getter=get_empty_environ,
                setup_settings=None,
            ),
            embryo_check.ExecutionExpectation.setup_phase_aware(
                main_result=asrt.is_none,
                instruction_settings=asrt_instr_settings.matches(
                    environ=asrt.equals(setup.as_dict(phase)),
                )
            ),
        ),
        NArrEx(
            'environ/non-existing (== None)',
            embryo_check.Arrangement.setup_phase_aware(
                process_execution_settings=
                proc_exe_env_for_test(
                    environ=None,
                ),
                default_environ_getter=get_environ_of_modified_before_action,
                setup_settings=None,
            ),
            embryo_check.ExecutionExpectation.setup_phase_aware(
                main_result=asrt.is_none,
                instruction_settings=asrt_instr_settings.matches(
                    environ=asrt.is_none,
                )
            ),
        ),
    ]


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
