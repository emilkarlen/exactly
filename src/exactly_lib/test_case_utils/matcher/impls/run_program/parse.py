from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.logic.matcher import MatcherSdv
from exactly_lib.test_case_utils.matcher.impls.run_program.run_conf import RunConfiguration, MODEL
from exactly_lib.test_case_utils.program.parse import parse_program


def parse(
        token_parser: TokenParser,
        run_conf: RunConfiguration[MODEL],
) -> MatcherSdv[MODEL]:
    program = parse_program.parse_program(token_parser, False)

    from . import sdv
    return sdv.sdv(run_conf, program)
