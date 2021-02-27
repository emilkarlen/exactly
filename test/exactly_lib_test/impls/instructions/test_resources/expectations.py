from typing import Sequence

from exactly_lib.symbol.sdv_structure import SymbolUsage
from exactly_lib.tcfs.sds import SandboxDs
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.test_case.phases.instruction_settings import InstructionSettings
from exactly_lib.test_case.result import svh
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings
from exactly_lib_test.test_case.result.test_resources import svh_assertions
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion


class ExpectationBase:
    def __init__(self,
                 validation_pre_sds: Assertion[svh.SuccessOrValidationErrorOrHardError]
                 = svh_assertions.is_success(),
                 main_side_effects_on_sds: Assertion[SandboxDs] = asrt.anything_goes(),
                 main_side_effects_on_tcds: Assertion[TestCaseDs] = asrt.anything_goes(),
                 symbol_usages: Assertion[Sequence[SymbolUsage]] = asrt.is_empty_sequence,
                 proc_exe_settings: Assertion[ProcessExecutionSettings]
                 = asrt.is_instance(ProcessExecutionSettings),
                 instruction_settings: Assertion[InstructionSettings]
                 = asrt.is_instance(InstructionSettings),
                 ):
        self._validation_pre_sds = svh_assertions.is_svh_and(validation_pre_sds)
        self._main_side_effects_on_sds = main_side_effects_on_sds
        self._main_side_effects_on_tcds = main_side_effects_on_tcds
        self._symbol_usages = symbol_usages
        self._proc_exe_settings = proc_exe_settings
        self._instruction_settings = instruction_settings

    @property
    def validation_pre_sds(self) -> Assertion[svh.SuccessOrValidationErrorOrHardError]:
        return self._validation_pre_sds

    @property
    def main_side_effects_on_sds(self) -> Assertion[SandboxDs]:
        return self._main_side_effects_on_sds

    @property
    def main_side_effects_on_tcds(self) -> Assertion[TestCaseDs]:
        return self._main_side_effects_on_tcds

    @property
    def symbol_usages(self) -> Assertion[Sequence[SymbolUsage]]:
        return self._symbol_usages

    @property
    def proc_exe_settings(self) -> Assertion[ProcessExecutionSettings]:
        return self._proc_exe_settings

    @property
    def instruction_settings(self) -> Assertion[InstructionSettings]:
        return self._instruction_settings
