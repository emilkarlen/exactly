from typing import Sequence, Generic

from exactly_lib.definitions import logic
from exactly_lib.section_document.element_parsers.ps_or_tp.parser import Parser
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.logic.matcher import MatcherSdv
from exactly_lib.test_case_utils.expression import grammar
from exactly_lib.test_case_utils.matcher.impls import quantifier_matchers
from exactly_lib.test_case_utils.matcher.impls.quantifier_matchers import MODEL, ELEMENT
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.logic_types import Quantifier
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser


def parse_after_quantifier_token(
        quantifier: Quantifier,
        element_predicate_parser: Parser[MatcherSdv[ELEMENT]],
        setup: quantifier_matchers.ElementSetup[MODEL, ELEMENT],
        token_parser: TokenParser,
) -> MatcherSdv[MODEL]:
    token_parser.consume_mandatory_constant_unquoted_string(
        setup.rendering.type_name,
        must_be_on_current_line=True)
    token_parser.consume_mandatory_constant_unquoted_string(
        logic.QUANTIFICATION_SEPARATOR_ARGUMENT,
        must_be_on_current_line=True)

    element_predicate = element_predicate_parser.parse_from_token_parser(token_parser)

    return quantifier_matchers.sdv(setup, quantifier, element_predicate)


class GrammarSetup(Generic[MODEL, ELEMENT]):
    def __init__(self,
                 element_setup: quantifier_matchers.ElementSetup[MODEL, ELEMENT],
                 element_predicate_parser: Parser[MatcherSdv[ELEMENT]],
                 ):
        self._setup = element_setup
        self._element_predicate_parser = element_predicate_parser

    def parse_all(self, parser: TokenParser) -> MatcherSdv[MODEL]:
        return parse_after_quantifier_token(Quantifier.ALL, self._element_predicate_parser, self._setup, parser)

    def parse_exists(self, parser: TokenParser) -> MatcherSdv[MODEL]:
        return parse_after_quantifier_token(Quantifier.EXISTS, self._element_predicate_parser, self._setup, parser)

    def quantification_grammar_expressions(self) -> Sequence[
        NameAndValue[grammar.PrimitiveExpression[MatcherSdv[MODEL]]]]:
        return (
            NameAndValue(
                logic.ALL_QUANTIFIER_ARGUMENT,
                grammar.PrimitiveExpression(
                    self.parse_all,
                    QuantificationDoc(Quantifier.ALL,
                                      self._setup.rendering.type_name,
                                      self._setup.rendering.element_matcher_syntax_name)
                )
            ),
            NameAndValue(
                logic.EXISTS_QUANTIFIER_ARGUMENT,
                grammar.PrimitiveExpression(
                    self.parse_exists,
                    QuantificationDoc(Quantifier.EXISTS,
                                      self._setup.rendering.type_name,
                                      self._setup.rendering.element_matcher_syntax_name)
                )
            ),
        )


class QuantificationDoc(grammar.PrimitiveExpressionDescriptionWithNameAsInitialSyntaxToken):
    def __init__(self,
                 quantifier: Quantifier,
                 element_name: str,
                 element_matcher_syntax_name: str,
                 ):
        self._quantifier = quantifier
        self._element_name = element_name
        self._element_matcher_syntax_name = element_matcher_syntax_name

    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        element_arg = a.Single(a.Multiplicity.MANDATORY,
                               a.Constant(self._element_name)
                               )
        separator_arg = a.Single(a.Multiplicity.MANDATORY,
                                 a.Constant(logic.QUANTIFICATION_SEPARATOR_ARGUMENT)
                                 )
        element_matcher_arg = a.Single(a.Multiplicity.MANDATORY,
                                       a.Named(self._element_matcher_syntax_name)
                                       )
        return (element_arg,
                separator_arg,
                element_matcher_arg,
                )

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        tp = TextParser({
            'quantifier_description': logic.QUANTIFIER_ARGUMENTS[self._quantifier],
            'element': self._element_name,
            'element_matcher': self._element_matcher_syntax_name,
        })

        return tp.fnap(_DESCRIPTION_OF_QUANTIFICATION)


_DESCRIPTION_OF_QUANTIFICATION = """\
Tests that {quantifier_description} {element} satisfies the given {element_matcher}.
"""
