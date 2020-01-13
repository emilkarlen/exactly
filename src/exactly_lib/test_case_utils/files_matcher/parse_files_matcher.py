from typing import Sequence, Dict, TypeVar

from exactly_lib.definitions import instruction_arguments, matcher_model
from exactly_lib.definitions.entity import syntax_elements, concepts, types
from exactly_lib.definitions.entity.syntax_elements import SyntaxElementInfo
from exactly_lib.definitions.entity.types import FILES_MATCHER_TYPE_INFO
from exactly_lib.definitions.primitives import files_matcher as files_matcher_primitives
from exactly_lib.processing import exit_values
from exactly_lib.section_document import parser_classes
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.logic.files_matcher import FilesMatcherSdv
from exactly_lib.test_case_utils.expression import grammar
from exactly_lib.test_case_utils.expression import parser as ep
from exactly_lib.test_case_utils.file_matcher import parse_file_matcher
from exactly_lib.test_case_utils.files_matcher.impl import emptiness, num_files, quant_over_files, sub_set_selection
from exactly_lib.test_case_utils.matcher import standard_expression_grammar
from exactly_lib.test_case_utils.matcher.impls import parse_quantified_matcher
from exactly_lib.type_system.logic.files_matcher import FilesMatcherSdvType
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.cli_syntax import option_syntax
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.logic_types import Quantifier, ExpectationType
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser


def files_matcher_parser() -> Parser[FilesMatcherSdv]:
    return parser_classes.ParserFromTokenParserFunction(parse_files_matcher,
                                                        consume_last_line_if_is_at_eol_after_parse=True)


def parse_files_matcher(parser: TokenParser,
                        must_be_on_current_line: bool = True) -> FilesMatcherSdv:
    return FilesMatcherSdv(parse_files_matcher__generic(parser, must_be_on_current_line))


def parse_files_matcher__generic(parser: TokenParser,
                                 must_be_on_current_line: bool = True) -> FilesMatcherSdvType:
    return ep.parse(GRAMMAR, parser, must_be_on_current_line)


def _file_quantified_assertion(quantifier: Quantifier,
                               parser: TokenParser) -> FilesMatcherSdvType:
    return parse_quantified_matcher.parse_after_quantifier_token(
        quantifier,
        parse_file_matcher.ParserOfGenericMatcherOnArbitraryLine(),
        quant_over_files.ELEMENT_SETUP,
        parser,
    )


def _parse_empty_check(parser: TokenParser) -> FilesMatcherSdvType:
    return emptiness.emptiness_matcher__generic()


def _parse_num_files_check(parser: TokenParser) -> FilesMatcherSdvType:
    return num_files.parse__generic(ExpectationType.POSITIVE, parser)


def _parse_selection(parser: TokenParser) -> FilesMatcherSdvType:
    element_matcher = parse_file_matcher.parse_sdv(parser, False)
    matcher_on_selection = parse_files_matcher__generic(parser, False)

    return sub_set_selection.sub_set_selection_matcher(element_matcher,
                                                       matcher_on_selection)


def _parse_file_quantified_assertion__all(parser: TokenParser) -> FilesMatcherSdvType:
    return _file_quantified_assertion(Quantifier.ALL, parser)


def _parse_file_quantified_assertion__exists(parser: TokenParser) -> FilesMatcherSdvType:
    return _file_quantified_assertion(Quantifier.EXISTS, parser)


class _EmptyDoc(grammar.SimpleExpressionDescription):
    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        return ()

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        return _TP.fnap(_CHECKS_THAT_PATH_IS_AN_EMPTY_DIRECTORY)


class _NumFilesDoc(grammar.SimpleExpressionDescription):
    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        return syntax_elements.INTEGER_MATCHER_SYNTAX_ELEMENT.single_mandatory,

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        return _TP.fnap(_CHECKS_THAT_DIRECTORY_CONTAINS_SPECIFIED_NUMBER_OF_FILES)


class _SelectionDoc(grammar.SimpleExpressionDescription):
    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        return (
            a.Single(a.Multiplicity.MANDATORY,
                     a.Named(instruction_arguments.SELECTION_OPTION.argument),
                     ),
            syntax_elements.FILES_MATCHER_SYNTAX_ELEMENT.single_mandatory,
        )

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        return _TP.fnap(_SELECTION_DESCRIPTION)


class _QuantificationDoc(grammar.SimpleExpressionDescription):
    def __init__(self,
                 quantifier: Quantifier,
                 element_name: str,
                 element_matcher: SyntaxElementInfo,
                 ):
        self._quantifier = quantifier
        self._element_name = element_name
        self._element_matcher = element_matcher

    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        element_arg = a.Single(a.Multiplicity.MANDATORY,
                               a.Constant(self._element_name)
                               )
        separator_arg = a.Single(a.Multiplicity.MANDATORY,
                                 a.Constant(instruction_arguments.QUANTIFICATION_SEPARATOR_ARGUMENT)
                                 )
        return (element_arg,
                separator_arg,
                self._element_matcher.single_mandatory,
                )

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        tp = TextParser({
            'quantifier_description': instruction_arguments.QUANTIFIER_ARGUMENTS[self._quantifier],
            'element': self._element_name,
            'element_matcher': self._element_matcher.singular_name,
        })

        return tp.fnap(_DESCRIPTION_OF_QUANTIFICATION)


_TP = TextParser({
    'symbol_concept': concepts.SYMBOL_CONCEPT_INFO.name,
    'selection': instruction_arguments.SELECTION.name,
    'file_matcher': types.FILE_MATCHER_TYPE_INFO.name.singular,
    'any': instruction_arguments.EXISTS_QUANTIFIER_ARGUMENT,
    'every': instruction_arguments.ALL_QUANTIFIER_ARGUMENT,
    'HARD_ERROR': exit_values.EXECUTION__HARD_ERROR.exit_identifier,
    'FILE_MATCHER': instruction_arguments.SELECTION_OPTION.argument,
    'FILE_MATCHER_SYNTAX_ELEMENT': syntax_elements.FILE_MATCHER_SYNTAX_ELEMENT.singular_name,
    'this_type': types.FILES_MATCHER_TYPE_INFO.name,
    'model': matcher_model.FILES_MATCHER_MODEL,
    'element': matcher_model.FILE_MATCHER_MODEL,
})

_MAIN_DESCRIPTION_REST = """\
Symbolic links are followed.
"""

_SELECTION_DESCRIPTION = """\
Makes the matcher apply to the sub set of {element:s} matched by {FILE_MATCHER}.
"""

_CHECKS_THAT_PATH_IS_AN_EMPTY_DIRECTORY = """\
Tests that the {model} is empty.
"""

_CHECKS_THAT_DIRECTORY_CONTAINS_SPECIFIED_NUMBER_OF_FILES = """\
Tests the number of {element:s}.
"""

_DESCRIPTION_OF_QUANTIFICATION = """\
Tests that {quantifier_description} {element} satisfies the given {element_matcher}.
"""

_SYMBOL_REF_DESCRIPTION = """\
Reference to {symbol_concept:a},
that must have been defined as {this_type:a}.
"""

MODEL = TypeVar('MODEL')


def _quantification_expressions(element_name: str,
                                element_matcher: SyntaxElementInfo,
                                ) -> Dict[str, grammar.SimpleExpression[FilesMatcherSdvType]]:
    return {
        instruction_arguments.ALL_QUANTIFIER_ARGUMENT:
            grammar.SimpleExpression(_parse_file_quantified_assertion__all,
                                     _QuantificationDoc(Quantifier.ALL, element_name, element_matcher)),

        instruction_arguments.EXISTS_QUANTIFIER_ARGUMENT:
            grammar.SimpleExpression(_parse_file_quantified_assertion__exists,
                                     _QuantificationDoc(Quantifier.EXISTS, element_name, element_matcher)),

    }


def _simple_expressions() -> Dict[str, grammar.SimpleExpression[FilesMatcherSdvType]]:
    ret_val = {
        files_matcher_primitives.EMPTINESS_CHECK_ARGUMENT:
            grammar.SimpleExpression(_parse_empty_check,
                                     _EmptyDoc()),

        files_matcher_primitives.NUM_FILES_CHECK_ARGUMENT:
            grammar.SimpleExpression(_parse_num_files_check,
                                     _NumFilesDoc()),

        option_syntax.option_syntax(instruction_arguments.SELECTION_OPTION.name):
            grammar.SimpleExpression(_parse_selection,
                                     _SelectionDoc()),

    }

    ret_val.update(_quantification_expressions(
        matcher_model.FILE_MATCHER_MODEL.singular,
        syntax_elements.FILE_MATCHER_SYNTAX_ELEMENT,
    ))

    return ret_val


GRAMMAR = standard_expression_grammar.new_grammar(
    concept=grammar.Concept(
        name=FILES_MATCHER_TYPE_INFO.name,
        type_system_type_name=FILES_MATCHER_TYPE_INFO.identifier,
        syntax_element_name=syntax_elements.FILES_MATCHER_SYNTAX_ELEMENT.argument,
    ),
    model=matcher_model.FILES_MATCHER_MODEL,
    value_type=ValueType.FILES_MATCHER,
    simple_expressions=_simple_expressions(),
)
