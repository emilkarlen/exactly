from exactly_lib.impls.types.matcher.impls.run_program.run_conf import RunConfiguration, MODEL
from exactly_lib.impls.types.program.parse import parse_program
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.type_val_deps.types.matcher import MatcherSdv


def parse(
        token_parser: TokenParser,
        run_conf: RunConfiguration[MODEL],
) -> MatcherSdv[MODEL]:
    program = _PROGRAM_PARSER.parse_from_token_parser(token_parser)

    from . import sdv
    return sdv.sdv(run_conf, program)


_PROGRAM_PARSER = parse_program.program_parser(must_be_on_current_line=False)
