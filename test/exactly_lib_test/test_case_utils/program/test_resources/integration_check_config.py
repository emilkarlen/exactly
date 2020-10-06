from typing import Generic

from exactly_lib.symbol.logic.program.program_sdv import ProgramSdv
from exactly_lib.type_system.logic.program.program import Program, ProgramDdv
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile
from exactly_lib_test.test_case_utils.logic.test_resources.common_properties_checker import INPUT, OUTPUT, \
    CommonPropertiesConfiguration, Applier
from exactly_lib_test.test_case_utils.logic.test_resources.logic_type_checker import LogicSdvPropertiesChecker, \
    WithTreeStructureExecutionPropertiesChecker
from exactly_lib_test.test_case_utils.program.test_resources.assertions import ResultWithTransformationData
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


class ProgramPropertiesConfiguration(Generic[INPUT, OUTPUT],
                                     CommonPropertiesConfiguration[Program,
                                                                   INPUT,
                                                                   OUTPUT]):
    def __init__(self, applier: Applier[Program, INPUT, OUTPUT]):
        self._applier = applier

    def applier(self) -> Applier[Program, ProcOutputFile, ResultWithTransformationData]:
        return self._applier

    def new_sdv_checker(self) -> LogicSdvPropertiesChecker[Program]:
        return LogicSdvPropertiesChecker(ProgramSdv)

    def new_execution_checker(self) -> WithTreeStructureExecutionPropertiesChecker[OUTPUT]:
        return WithTreeStructureExecutionPropertiesChecker(ProgramDdv, Program, asrt.anything_goes())
