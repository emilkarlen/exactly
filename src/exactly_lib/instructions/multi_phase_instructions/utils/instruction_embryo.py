from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, PhaseLoggingPaths
from exactly_lib.test_case_utils.pre_or_post_validation import PreOrPostSdsValidator, ConstantSuccessValidator


class MainStepExecutorEmbryo:
    """
    Executor with standard arguments, but custom return type.
    
    The custom return type makes testing easier, by providing access to
    custom result.
    """

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             logging_paths: PhaseLoggingPaths,
             os_services: OsServices):
        raise NotImplementedError()


class InstructionEmbryo(MainStepExecutorEmbryo):
    """
    Instruction embryo that makes it easy to both
    test using custom information (in sub classes),
    and integrate into many phases.
    
    A multi-phase instruction may sub class this class,
    to achieve both easy testing (by giving access to things that
    are specific for the instruction in question),
    and integrate into different phases.
    """

    @property
    def symbol_usages(self) -> list:
        return []

    @property
    def validator(self) -> PreOrPostSdsValidator:
        return ConstantSuccessValidator()


class InstructionEmbryoParser:
    def parse(self, source: ParseSource) -> InstructionEmbryo:
        raise NotImplementedError()


class InstructionEmbryoParserThatConsumesCurrentLine(InstructionEmbryoParser):
    """
    A parser that unconditionally consumes the current line,
    and that uses the remaining part of the current line for
    constructing the parsed instruction.

    The parser cannot consume any more than the current line.

    Precondition: The source must have a current line.
    """

    def parse(self, source: ParseSource) -> InstructionEmbryo:
        rest_of_line = source.remaining_part_of_current_line
        source.consume_current_line()
        return self._parse(rest_of_line)

    def _parse(self, rest_of_line: str) -> InstructionEmbryo:
        raise NotImplementedError()
