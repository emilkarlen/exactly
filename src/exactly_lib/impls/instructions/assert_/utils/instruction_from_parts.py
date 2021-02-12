from typing import Sequence

from exactly_lib.impls.instructions.multi_phase.utils.instruction_parts import InstructionParts, \
    InstructionPartsParser
from exactly_lib.impls.svh_validators import PreOrPostSdsSvhValidationErrorValidator
from exactly_lib.section_document.element_parsers.section_element_parsers import \
    InstructionParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.source_location import FileSystemLocationInfo
from exactly_lib.symbol.sdv_structure import SymbolUsage
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.instruction_settings import InstructionSettings
from exactly_lib.test_case.result import pfh, svh


class AssertPhaseInstructionFromParts(AssertPhaseInstruction):
    def __init__(self, parts: InstructionParts):
        self._parts = parts
        self._validator = PreOrPostSdsSvhValidationErrorValidator(parts.validator)

    def symbol_usages(self) -> Sequence[SymbolUsage]:
        return self._parts.symbol_usages

    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep
                         ) -> svh.SuccessOrValidationErrorOrHardError:
        return self._validator.validate_pre_sds_if_applicable(environment.path_resolving_environment)

    def validate_post_setup(self,
                            environment: InstructionEnvironmentForPostSdsStep
                            ) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             settings: InstructionSettings,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        validation_result = self._validator.validate_post_sds_if_applicable(environment.path_resolving_environment)
        if not validation_result.is_success:
            return pfh.new_pfh_hard_error(validation_result.failure_message)

        return self._parts.executor.apply_as_assertion(environment, settings, os_services)


class Parser(InstructionParser):
    def __init__(self, instruction_parts_parser: InstructionPartsParser):
        self.instruction_parts_parser = instruction_parts_parser

    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              source: ParseSource) -> AssertPhaseInstruction:
        instruction_parts = self.instruction_parts_parser.parse(fs_location_info, source)
        return AssertPhaseInstructionFromParts(instruction_parts)
