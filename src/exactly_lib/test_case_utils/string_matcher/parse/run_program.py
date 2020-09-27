from typing import Sequence

from exactly_lib.definitions import misc_texts, matcher_model
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.test_case_utils.matcher.impls.run_program import documentation
from exactly_lib.test_case_utils.program.parse import parse_program
from exactly_lib.type_system.logic.string_matcher import StringMatcherSdv
from exactly_lib.util.textformat.structure.core import ParagraphItem


def parse(token_parser: TokenParser) -> StringMatcherSdv:
    program = _PROGRAM_PARSER.parse_from_token_parser(token_parser)

    from exactly_lib.test_case_utils.string_matcher.impl import run_program
    return run_program.sdv(program)


class SyntaxDescription(documentation.SyntaxDescriptionBase):
    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        from exactly_lib.test_case_utils.matcher import help_texts
        from exactly_lib.util.textformat.textformat_parser import TextParser
        tp = TextParser({
            'MODEL': matcher_model.STRING_MATCHER_MODEL,
            'stdin': misc_texts.STDIN,
        })
        return help_texts.run_program_matcher_description(
            tp.fnap(_EXE_ENV_DESCRIPTION)
        )


_PROGRAM_PARSER = parse_program.program_parser(
    must_be_on_current_line=False,
)

_EXE_ENV_DESCRIPTION = """\
The {MODEL} to match is given as {stdin}.
"""
