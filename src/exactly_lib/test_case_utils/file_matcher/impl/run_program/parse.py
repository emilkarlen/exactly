from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.test_case_utils.program.parse import parse_program
from exactly_lib.type_system.logic.file_matcher import FileMatcherSdv


def parse(token_parser: TokenParser) -> FileMatcherSdv:
    program = parse_program.parse_program(token_parser, False)

    from exactly_lib.test_case_utils.matcher.impls.run_program import sdv
    from . import runner
    return sdv.sdv(runner.FileMatcherRunner, program)
