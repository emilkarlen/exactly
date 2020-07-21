from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.logic.matcher import MatcherSdv
from exactly_lib.test_case_utils.matcher.impls.run_program.run_conf import RunConfiguration, MODEL
from exactly_lib.test_case_utils.program.parse import parse_program


def parse(
        token_parser: TokenParser,
        run_conf: RunConfiguration[MODEL],
) -> MatcherSdv[MODEL]:
    program = _PROGRAM_PARSER.parse_from_token_parser(token_parser)

    from . import sdv
    return sdv.sdv(run_conf, program)


_PROGRAM_PARSER = parse_program.program_parser(must_be_on_current_line=False)
