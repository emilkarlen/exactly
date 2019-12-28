from exactly_lib.definitions import instruction_arguments
from exactly_lib.definitions.entity import syntax_elements, concepts
from exactly_lib.definitions.primitives import files_matcher as files_matcher_primitives
from exactly_lib.section_document import parser_classes
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol import symbol_syntax
from exactly_lib.symbol.logic.files_matcher import FilesMatcherSdv
from exactly_lib.test_case_utils.file_matcher import parse_file_matcher
from exactly_lib.test_case_utils.files_matcher.impl import emptiness, num_files, quant_over_files, sub_set_selection
from exactly_lib.test_case_utils.files_matcher.impl import symbol_reference
from exactly_lib.test_case_utils.matcher.impls import parse_quantified_matcher, combinator_sdvs
from exactly_lib.type_system.logic.files_matcher import FilesMatcherSdvType
from exactly_lib.util.logic_types import Quantifier, ExpectationType


def files_matcher_parser() -> Parser[FilesMatcherSdv]:
    return parser_classes.ParserFromTokenParserFunction(parse_files_matcher,
                                                        consume_last_line_if_is_at_eol_after_parse=False)


def parse_files_matcher(parser: TokenParser,
                        must_be_on_current_line: bool = True) -> FilesMatcherSdv:
    if must_be_on_current_line:
        parser.require_is_not_at_eol('Missing ' + syntax_elements.FILES_MATCHER_SYNTAX_ELEMENT.singular_name)

    mb_file_selector = parse_file_matcher.parse_optional_selection_sdv2(parser)
    expectation_type = parser.consume_optional_negation_operator()

    ret_val = _SIMPLE_MATCHER_PARSER.parse(parser)

    if expectation_type is ExpectationType.NEGATIVE:
        ret_val = combinator_sdvs.Negation(ret_val)

    if mb_file_selector is not None:
        ret_val = sub_set_selection.sub_set_selection_matcher(mb_file_selector,
                                                              ret_val)

    return FilesMatcherSdv(ret_val)


class _SimpleMatcherParser:
    def __init__(self):
        self.matcher_parsers = {
            files_matcher_primitives.NUM_FILES_CHECK_ARGUMENT: self.parse_num_files_check,
            files_matcher_primitives.EMPTINESS_CHECK_ARGUMENT: self.parse_empty_check,
            instruction_arguments.ALL_QUANTIFIER_ARGUMENT: self.parse_file_quantified_assertion__all,
            instruction_arguments.EXISTS_QUANTIFIER_ARGUMENT: self.parse_file_quantified_assertion__exists,
        }

    def parse(self, parser: TokenParser) -> FilesMatcherSdvType:
        matcher_name = parser.consume_mandatory_unquoted_string(
            syntax_elements.FILES_MATCHER_SYNTAX_ELEMENT.singular_name,
            False)
        if matcher_name in self.matcher_parsers:
            return self.matcher_parsers[matcher_name](parser)
        else:
            return self.parse_symbol_reference(matcher_name, parser)

    def parse_empty_check(self, parser: TokenParser) -> FilesMatcherSdvType:
        return emptiness.emptiness_matcher__generic()

    def parse_num_files_check(self, parser: TokenParser) -> FilesMatcherSdvType:
        return num_files.parse__generic(ExpectationType.POSITIVE, parser)

    def parse_file_quantified_assertion__all(self, parser: TokenParser) -> FilesMatcherSdvType:
        return self._file_quantified_assertion(Quantifier.ALL, parser)

    def parse_file_quantified_assertion__exists(self, parser: TokenParser) -> FilesMatcherSdvType:
        return self._file_quantified_assertion(Quantifier.EXISTS, parser)

    def parse_symbol_reference(self, parsed_symbol_name: str, parser: TokenParser) -> FilesMatcherSdvType:
        if symbol_syntax.is_symbol_name(parsed_symbol_name):
            return symbol_reference.symbol_reference_matcher(parsed_symbol_name)
        else:
            err_msg_header = 'Neither a {matcher} nor the plain name of a {symbol}: '.format(
                matcher=syntax_elements.FILES_MATCHER_SYNTAX_ELEMENT.singular_name,
                symbol=concepts.SYMBOL_CONCEPT_INFO.singular_name)
            raise SingleInstructionInvalidArgumentException(err_msg_header + parsed_symbol_name)

    def _file_quantified_assertion(self,
                                   quantifier: Quantifier,
                                   parser: TokenParser) -> FilesMatcherSdvType:
        return parse_quantified_matcher.parse_after_quantifier_token(
            quantifier,
            parse_file_matcher.ParserOfGenericMatcherOnArbitraryLine(),
            quant_over_files.ELEMENT_SETUP,
            parser,
        )


_SIMPLE_MATCHER_PARSER = _SimpleMatcherParser()
