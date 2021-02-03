from typing import Tuple

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.impls.program_execution.processors.store_result_in_files import ExitCodeAndStderrFile
from exactly_lib.impls.types.integer_matcher import parse_integer_matcher
from exactly_lib.impls.types.program.parse import parse_program
from exactly_lib.section_document.element_parsers import token_stream_parser
from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.source_location import FileSystemLocationInfo
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from . import defs
from .impl import texts, doc
from .impl.exit_code import getter_from_atc, getter_from_program
from .impl.exit_code.instruction import instruction as _instruction
from ..utils.instruction_of_matcher import ModelGetterSdv


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        Parser(),
        doc.for_exit_code(instruction_name))


class Parser(InstructionParser):
    def __init__(self):
        self._matcher_parser = parse_integer_matcher.parsers(False).full
        self._program_parser = parse_program.program_parser(must_be_on_current_line=False)

    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              source: ParseSource) -> AssertPhaseInstruction:
        with token_stream_parser.from_parse_source(source,
                                                   consume_last_line_if_is_at_eol_after_parse=True) as token_parser:
            object_name, model_getter = self._parse_setup(token_parser)
            int_matcher = self._matcher_parser.parse_from_token_parser(token_parser)

            token_parser.report_superfluous_arguments_if_not_at_eol()

            return _instruction(object_name, int_matcher, model_getter)

    def _parse_setup(self, token_parser: TokenParser) -> Tuple[str, ModelGetterSdv[ExitCodeAndStderrFile]]:
        if token_parser.consume_optional_option(defs.OUTPUT_FROM_PROGRAM_OPTION_NAME):
            program = self._program_parser.parse_from_token_parser(token_parser)
            return texts.OBJECT__PROGRAM, getter_from_program.model_getter(program)
        else:
            return texts.OBJECT__ATC, getter_from_atc.model_getter()
