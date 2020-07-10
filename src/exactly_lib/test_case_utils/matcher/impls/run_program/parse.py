from typing import Callable

from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.logic.matcher import MatcherSdv
from exactly_lib.test_case_utils.matcher.impls.run_program.runner import Runner, MODEL
from exactly_lib.test_case_utils.program.parse import parse_program
from exactly_lib.type_system.logic.application_environment import ApplicationEnvironment


def parse(
        token_parser: TokenParser,
        mk_runner: Callable[[ApplicationEnvironment], Runner[MODEL]],
) -> MatcherSdv[MODEL]:
    program = parse_program.parse_program(token_parser, False)

    from . import sdv
    return sdv.sdv(mk_runner, program)
