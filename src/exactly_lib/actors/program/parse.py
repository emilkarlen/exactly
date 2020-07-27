from typing import Sequence

from exactly_lib.actors.program.executable_object import ProgramToExecute
from exactly_lib.actors.util import source_code_lines_utils
from exactly_lib.actors.util.executor_made_of_parts.parts import ExecutableObjectParser
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.section_document import parse_source
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.symbol.logic.program.program_sdv import ProgramSdv
from exactly_lib.test_case.actor import ParseException
from exactly_lib.test_case.phases.act import ActPhaseInstruction
from exactly_lib.test_case.result import svh
from exactly_lib.test_case_utils.program.parse import parse_program
from ..common import relativity_configuration_of_action_to_check
from ...definitions import instruction_arguments


class Parser(ExecutableObjectParser[ProgramToExecute]):
    def __init__(self):
        self._program_parser = parse_program.program_parser(
            exe_file_relativity=relativity_configuration_of_action_to_check(
                instruction_arguments.PATH_SYNTAX_ELEMENT_NAME
            )
        )

    def apply(self, instructions: Sequence[ActPhaseInstruction]) -> ProgramToExecute:
        source_str = source_code_lines_utils.all_lines_str(instructions)
        parse_src = parse_source.ParseSource(source_str)

        _consume_until_first_source_code_line_or_eof(parse_src)
        program = self._parse_program(parse_src)
        _syntax_error_if_not_at_eof(parse_src)

        return ProgramToExecute(program)

    def _parse_program(self, source: parse_source.ParseSource) -> ProgramSdv:
        try:
            return self._program_parser.parse(source)
        except SingleInstructionInvalidArgumentException as ex:
            raise ParseException(
                svh.new_svh_validation_error__str(ex.error_message)
            )


def _consume_until_first_source_code_line_or_eof(source: parse_source.ParseSource):
    while source.has_current_line and \
            not source_code_lines_utils.is_source_code_line(source.remaining_part_of_current_line):
        source.consume_current_line()


def _syntax_error_if_not_at_eof(source: parse_source.ParseSource):
    _consume_until_first_source_code_line_or_eof(source)
    if not source.is_at_eof:
        raise ParseException(svh.new_svh_validation_error__str(
            'Superfluous arguments of {PROGRAM}: {src}'.format(
                PROGRAM=syntax_elements.PROGRAM_SYNTAX_ELEMENT.singular_name,
                src=source.remaining_part_of_current_line
            )
        )
        )
