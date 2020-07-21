from typing import Optional

from exactly_lib.definitions.primitives import file_matcher
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.test_case_utils.file_matcher.impl.run_program import arguments_generator
from exactly_lib.test_case_utils.program.parse import parse_program
from exactly_lib.type_system.logic.file_matcher import FileMatcherSdv


def parse(token_parser: TokenParser) -> FileMatcherSdv:
    args_generator = _parse_arguments_generator(token_parser)
    program = _PROGRAM_PARSER.parse_from_token_parser(token_parser)

    from exactly_lib.test_case_utils.matcher.impls.run_program import sdv
    from . import run_conf

    return sdv.sdv(run_conf.FileMatcherRunConfiguration(args_generator),
                   program)


_PROGRAM_PARSER = parse_program.program_parser(
    must_be_on_current_line=False,
)


def _parse_arguments_generator(token_parser: TokenParser) -> arguments_generator.ArgumentsGenerator:
    return token_parser.consume_and_handle_first_matching_option_2(
        _default_arg_pos(),
        [
            (file_matcher.PROGRAM_ARG_OPTION__LAST, _mk_arg_pos__last),
            (file_matcher.PROGRAM_ARG_OPTION__MARKER, _mk_arg_pos__marker),
        ]
    )


def _mk_arg_pos__last(option_argument: Optional[str]) -> arguments_generator.ArgumentsGenerator:
    return arguments_generator.Last()


def _mk_arg_pos__marker(option_argument: Optional[str]) -> arguments_generator.ArgumentsGenerator:
    return arguments_generator.Marker(option_argument)


def _default_arg_pos() -> arguments_generator.ArgumentsGenerator:
    return arguments_generator.Last()
