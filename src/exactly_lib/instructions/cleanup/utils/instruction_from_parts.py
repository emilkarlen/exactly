from typing import Sequence

from exactly_lib.instructions.multi_phase.utils.instruction_parts import InstructionParts, \
    InstructionPartsParser
from exactly_lib.section_document.element_parsers.section_element_parsers import \
    InstructionParserWithoutFileReferenceRelativityRoot
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.symbol_usage import SymbolUsage
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.cleanup import CleanupPhaseInstruction, PreviousPhase
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.pre_or_post_validation import PreOrPostSdsSvhValidationErrorValidator, \
    PreOrPostSdsSvhValidationForSuccessOrHardError
from exactly_lib.test_case.result import sh, svh


class CleanupPhaseInstructionFromParts(CleanupPhaseInstruction):
    def __init__(self,
                 instruction_setup: InstructionParts):
        self.setup = instruction_setup
        self._validator = PreOrPostSdsSvhValidationErrorValidator(instruction_setup.validator)

    def symbol_usages(self) -> Sequence[SymbolUsage]:
        return self.setup.symbol_usages

    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        validator = PreOrPostSdsSvhValidationErrorValidator(self.setup.validator)
        return validator.validate_pre_sds_if_applicable(environment.path_resolving_environment)

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices,
             previous_phase: PreviousPhase) -> sh.SuccessOrHardError:
        validation_result = self._validate_from_main(environment)
        if validation_result.is_hard_error:
            return validation_result
        return self.setup.executor.apply_as_non_assertion(environment,
                                                          environment.phase_logging,
                                                          os_services)

    def _validate_from_main(
            self,
            environment: InstructionEnvironmentForPostSdsStep) -> sh.SuccessOrHardError:
        validator = PreOrPostSdsSvhValidationForSuccessOrHardError(self.setup.validator)
        return validator.validate_post_sds_if_applicable(environment.path_resolving_environment_pre_or_post_sds)


class Parser(InstructionParserWithoutFileReferenceRelativityRoot):
    def __init__(self, instruction_parts_parser: InstructionPartsParser):
        self.instruction_parts_parser = instruction_parts_parser

    def parse_from_source(self, source: ParseSource) -> CleanupPhaseInstruction:
        instruction_parts = self.instruction_parts_parser.parse(source)
        return CleanupPhaseInstructionFromParts(instruction_parts)
