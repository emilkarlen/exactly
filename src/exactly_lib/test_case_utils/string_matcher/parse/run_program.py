from typing import Sequence

from exactly_lib.definitions import misc_texts, matcher_model
from exactly_lib.definitions.entity import syntax_elements, types
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.test_case_utils.matcher.impls.run_program import documentation
from exactly_lib.test_case_utils.program.parse import parse_program
from exactly_lib.type_system.logic.string_matcher import StringMatcherSdv
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser


def parse(token_parser: TokenParser) -> StringMatcherSdv:
    program = _PROGRAM_PARSER.parse_from_token_parser(token_parser)

    from exactly_lib.test_case_utils.string_matcher.impl import run_program
    return run_program.sdv(program)


class SyntaxDescription(documentation.SyntaxDescriptionBase):
    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        return _TP.fnap(_RUN_MATCHER_SED_DESCRIPTION)


_PROGRAM_PARSER = parse_program.program_parser(
    must_be_on_current_line=False,
)

_TP = TextParser({
    'program': types.PROGRAM_TYPE_INFO.name,
    'PROGRAM': syntax_elements.PROGRAM_SYNTAX_ELEMENT.singular_name,
    'MODEL': matcher_model.STRING_MATCHER_MODEL,
    'exit_code': misc_texts.EXIT_CODE,
    'stdin': misc_texts.STDIN,
})

_RUN_MATCHER_SED_DESCRIPTION = """\
Runs {program:a}. Matches iff the {exit_code} is 0.


The {MODEL} to match is given as {stdin}.


Transformations of the output from {PROGRAM} are ignored.
"""
