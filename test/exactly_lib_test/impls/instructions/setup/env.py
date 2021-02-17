import unittest
from typing import Mapping, Optional

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.impls.instructions.multi_phase.environ.impl import Phase
from exactly_lib.impls.instructions.setup import env as sut
from exactly_lib.test_case.phases.setup.settings_builder import SetupSettingsBuilder
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.impls.instructions.multi_phase.environ.test_resources.abstract_syntax import \
    SetVariableArgumentsAbsStx, UnsetVariableArgumentsAbsStx
from exactly_lib_test.impls.instructions.multi_phase.environ.test_resources.env_instruction_test import \
    suite_for_setup_phase
from exactly_lib_test.impls.instructions.setup.test_resources import instruction_check
from exactly_lib_test.impls.instructions.setup.test_resources.configuration import SetupConfigurationBase
from exactly_lib_test.impls.instructions.setup.test_resources.instruction_check import Arrangement, \
    MultiSourceExpectation
from exactly_lib_test.test_case.test_resources import instr_settings_assertions as asrt_instr_settings
from exactly_lib_test.test_case.test_resources import settings_builder_assertions as asrt_setup_settings
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.process_execution.test_resources.proc_exe_env import proc_exe_env_for_test


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        suite_for_setup_phase(TheConfiguration()),
        TestSetOfAllPhases(),
        TestSetOfActPhases(),
        TestUnsetExistingVariableOfAllPhases(),
        TestUnsetExistingVariableOfActPhases(),
    ])


class TheConfiguration(SetupConfigurationBase):
    def instruction_setup(self) -> SingleInstructionSetup:
        return sut.setup('instruction name')


class TestSetOfAllPhases(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        var_val = NameAndValue('name', 'value')
        instruction_argument = SetVariableArgumentsAbsStx.of_nav(var_val,
                                                                 phase_spec=None)
        expected_environ = {var_val.name: var_val.value}

        env_before_modification = {}

        # ACT & ASSERT #
        CHECKER.check_multi_source__abs_stx(
            self,
            instruction_argument,
            arr(
                env_before_modification,
                env_before_modification,
            ),
            expect(
                expected_environ,
                expected_environ,
            ),
        )


class TestSetOfActPhases(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        var_val = NameAndValue('name', 'value')
        instruction_argument = SetVariableArgumentsAbsStx.of_nav(var_val,
                                                                 phase_spec=Phase.ACT)
        expected_environ = {var_val.name: var_val.value}

        env_before_modification = {}

        # ACT & ASSERT #
        CHECKER.check_multi_source__abs_stx(
            self,
            instruction_argument,
            arr(
                env_before_modification,
                env_before_modification,
            ),
            expect(
                instruction_settings=env_before_modification,
                setup_settings=expected_environ,
            ),
        )


class TestUnsetExistingVariableOfAllPhases(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        var_name = 'var_to_unset'
        other_var = NameAndValue('other_var', 'val of other var')
        instruction_argument = UnsetVariableArgumentsAbsStx.of_str(var_name, phase_spec=None)
        environ_w_var_to_unset = {var_name: 'value of var to unset',
                                  other_var.name: other_var.value}
        environ_wo_var_to_unset = {other_var.name: other_var.value}

        # ACT & ASSERT #
        CHECKER.check_multi_source__abs_stx(
            self,
            instruction_argument,
            arr(
                environ_w_var_to_unset,
                environ_w_var_to_unset,
            ),
            expect(
                environ_wo_var_to_unset,
                environ_wo_var_to_unset,
            ),
        )


class TestUnsetExistingVariableOfActPhases(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        var_name = 'var_to_unset'
        other_var = NameAndValue('other_var', 'val of other var')
        instruction_argument = UnsetVariableArgumentsAbsStx.of_str(var_name, phase_spec=Phase.ACT)
        environ_w_var_to_unset = {var_name: 'value of var to unset',
                                  other_var.name: other_var.value}
        environ_wo_var_to_unset = {other_var.name: other_var.value}

        # ACT & ASSERT #
        CHECKER.check_multi_source__abs_stx(
            self,
            instruction_argument,
            arr(
                environ_w_var_to_unset,
                environ_w_var_to_unset,
            ),
            expect(
                instruction_settings=environ_w_var_to_unset,
                setup_settings=environ_wo_var_to_unset,
            ),
        )


def arr(instruction_settings: Optional[Mapping[str, str]],
        setup_settings: Optional[Mapping[str, str]],
        ) -> Arrangement:
    return Arrangement(
        process_execution_settings=proc_exe_env_for_test(
            environ=dict(instruction_settings),
        ),
        settings_builder=SetupSettingsBuilder(
            environ=dict(setup_settings),
            stdin=None,
        )
    )


def expect(instruction_settings: Optional[Mapping[str, str]],
           setup_settings: Optional[Mapping[str, str]],
           ) -> MultiSourceExpectation:
    return MultiSourceExpectation(
        instruction_settings=asrt_instr_settings.matches(
            environ=asrt.equals(instruction_settings),
        ),
        settings_builder=asrt_setup_settings.matches(
            environ=asrt.equals(setup_settings),
            stdin=asrt.is_none,
        )
    )


CHECKER = instruction_check.Checker(sut.setup('the instruction name'))

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
