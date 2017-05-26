from exactly_lib.instructions.multi_phase_instructions.utils.instruction_parts import InstructionParts, \
    InstructionInfoForConstructingAnInstructionFromParts
from exactly_lib.instructions.multi_phase_instructions.utils.parser import InstructionPartsParser
from exactly_lib.instructions.utils.pre_or_post_validation import PreOrPostSdsSvhValidationErrorValidator
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.section_element_parsers import InstructionParser
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.result import pfh
from exactly_lib.test_case.phases.result import svh


class AssertPhaseInstructionFromParts(AssertPhaseInstruction):
    def __init__(self,
                 instruction_setup: InstructionParts):
        self.setup = instruction_setup
        self._validator = PreOrPostSdsSvhValidationErrorValidator(instruction_setup.validator)

    def symbol_usages(self) -> list:
        return self.setup.symbol_usages

    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep
                         ) -> svh.SuccessOrValidationErrorOrHardError:
        return self._validator.validate_pre_sds_if_applicable(environment.path_resolving_environment)

    def validate_post_setup(self,
                            environment: InstructionEnvironmentForPostSdsStep
                            ) -> svh.SuccessOrValidationErrorOrHardError:
        return self._validator.validate_post_sds_if_applicable(environment.path_resolving_environment)

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        return self.setup.executor.apply_as_assertion(environment,
                                                      environment.phase_logging,
                                                      os_services)


class Parser(InstructionParser):
    def __init__(self, instruction_parts_parser: InstructionPartsParser):
        self.instruction_parts_parser = instruction_parts_parser

    def parse(self, source: ParseSource) -> AssertPhaseInstruction:
        instruction_parts = self.instruction_parts_parser.parse(source)
        return AssertPhaseInstructionFromParts(instruction_parts)


def instruction_info_for(instruction_name: str) -> InstructionInfoForConstructingAnInstructionFromParts:
    return InstructionInfoForConstructingAnInstructionFromParts(instruction_name,
                                                                AssertPhaseInstructionFromParts)
