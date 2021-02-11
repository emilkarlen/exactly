from exactly_lib.tcfs.sds import SandboxDs
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.test_case.phases.instruction_settings import InstructionSettings
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings
from exactly_lib_test.test_case.result.test_resources import svh_assertions
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion


class ExpectationBase:
    def __init__(self,
                 validation_pre_sds: Assertion,
                 main_side_effects_on_sds: Assertion[SandboxDs],
                 main_side_effects_on_tcds: Assertion[TestCaseDs],
                 symbol_usages: Assertion,
                 proc_exe_settings: Assertion[ProcessExecutionSettings],
                 instruction_settings: Assertion[InstructionSettings],
                 ):
        self.validation_pre_sds = svh_assertions.is_svh_and(validation_pre_sds)
        self.main_side_effects_on_sds = main_side_effects_on_sds
        self.main_side_effects_on_tcds = main_side_effects_on_tcds
        self.symbol_usages = symbol_usages
        self.proc_exe_settings = proc_exe_settings
        self.instruction_settings = instruction_settings
