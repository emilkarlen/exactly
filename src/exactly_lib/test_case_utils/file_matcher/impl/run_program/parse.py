from typing import Optional

from exactly_lib.definitions.primitives import file_matcher
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.test_case_utils.file_matcher.impl.run_program import arguments_generator
from exactly_lib.test_case_utils.program.parse import parse_program
from exactly_lib.type_system.logic.application_environment import ApplicationEnvironment
from exactly_lib.type_system.logic.file_matcher import FileMatcherSdv, FileMatcherModel


def parse(token_parser: TokenParser) -> FileMatcherSdv:
    args_generator = _parse_arguments_generator(token_parser)
    program = parse_program.parse_program(token_parser, False)

    from exactly_lib.test_case_utils.matcher.impls.run_program import sdv
    from . import runner

    def mk_runner(application_environment: ApplicationEnvironment) -> runner.Runner[FileMatcherModel]:
        return runner.FileMatcherRunner(args_generator, application_environment)

    return sdv.sdv(mk_runner, program)


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
