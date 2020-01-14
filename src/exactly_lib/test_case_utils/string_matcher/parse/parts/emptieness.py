from typing import Sequence

from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.logic.string_matcher import StringMatcherSdv
from exactly_lib.test_case_utils.expression import grammar
from exactly_lib.test_case_utils.matcher.impls import combinator_sdvs
from exactly_lib.test_case_utils.string_matcher.impl import emptiness
from exactly_lib.type_system.logic.string_matcher import GenericStringMatcherSdv
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser


def parse(expectation_type: ExpectationType,
          token_parser: TokenParser) -> StringMatcherSdv:
    return StringMatcherSdv(
        combinator_sdvs.of_expectation_type(
            parse__generic(token_parser),
            expectation_type
        ),
    )


def parse__generic(token_parser: TokenParser) -> GenericStringMatcherSdv:
    return emptiness.sdv__generic()


class Description(grammar.SimpleExpressionDescription):
    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        return ()

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        return TextParser().fnap(_DESCRIPTION_OF_EMPTY)


_DESCRIPTION_OF_EMPTY = """\
Matches if the string is empty.
"""
