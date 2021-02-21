import re
from typing import Sequence, Set, Pattern, Optional

from exactly_lib.common.report_rendering import text_docs
from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.impls.description_tree import custom_details
from exactly_lib.impls.types.regex.regex_ddv import RegexSdv, RegexDdv
from exactly_lib.impls.types.string_.parse_string_or_here_doc import parse_string_or_here_doc_from_token_parser
from exactly_lib.section_document.element_parsers.ps_or_tp import parsers
from exactly_lib.section_document.element_parsers.ps_or_tp.parser import Parser
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser, ParserFromTokens
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.tcfs.hds import HomeDs
from exactly_lib.tcfs.path_relativity import DirectoryStructurePartition
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import DdvValidator
from exactly_lib.type_val_deps.types.string_.string_ddv import StringDdv
from exactly_lib.type_val_deps.types.string_.string_sdv import StringSdv
from exactly_lib.util.cli_syntax import option_syntax
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.description_tree import details
from exactly_lib.util.description_tree.renderer import DetailsRenderer
from exactly_lib.util.render import strings as string_rendering
from exactly_lib.util.str_ import str_constructor
from exactly_lib.util.symbol_table import SymbolTable

IGNORE_CASE_OPTION_NAME = a.OptionName(long_name='ignore-case')

IGNORE_CASE_OPTION = option_syntax.option_syntax(IGNORE_CASE_OPTION_NAME)

MISSING_REGEX_ARGUMENT_ERR_MSG = 'Missing ' + syntax_elements.REGEX_SYNTAX_ELEMENT.argument.name

MISSING_STRING_ARGUMENT_FOR_REGEX_ERR_MSG = 'Missing {} argument for {}'.format(
    syntax_elements.STRING_SYNTAX_ELEMENT.argument.name,
    syntax_elements.REGEX_SYNTAX_ELEMENT.argument.name,
)


def regex_parser() -> Parser[RegexSdv]:
    return _PARSER


class ParserOfRegex(ParserFromTokens[RegexSdv]):
    def parse(self, token_parser: TokenParser) -> RegexSdv:
        return parse_regex2(token_parser,
                            must_be_on_same_line=False,
                            consume_last_here_doc_line=False)


def parse_regex(parser: TokenParser,
                must_be_on_same_line: bool = True,
                consume_last_here_doc_line: bool = False) -> RegexSdv:
    return parse_regex2(parser, must_be_on_same_line, consume_last_here_doc_line)


def parse_regex2(parser: TokenParser,
                 must_be_on_same_line: bool = True,
                 consume_last_here_doc_line: bool = False) -> RegexSdv:
    if must_be_on_same_line:
        parser.require_is_not_at_eol(MISSING_REGEX_ARGUMENT_ERR_MSG)

    is_ignore_case = parser.consume_and_handle_optional_option(False,
                                                               lambda x: True,
                                                               IGNORE_CASE_OPTION_NAME)
    if must_be_on_same_line:
        parser.require_is_not_at_eol(MISSING_REGEX_ARGUMENT_ERR_MSG)

    regex_pattern = parse_string_or_here_doc_from_token_parser(parser,
                                                               consume_last_here_doc_line)
    return _RegexSdv(is_ignore_case, regex_pattern)


_PARSER = parsers.ParserFromTokenParserFunction(parse_regex)


class _RegexSdv(RegexSdv):
    def __init__(self,
                 is_ignore_case: bool,
                 string: StringSdv):
        self._is_ignore_case = is_ignore_case
        self._string = string
        self._value = None

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._string.references

    def resolve(self, symbols: SymbolTable) -> RegexDdv:
        return _RegexDdv(self._is_ignore_case,
                         self._string.resolve(symbols))


class _ValidatorWhichCreatesRegex(DdvValidator):
    def __init__(self,
                 is_ignore_case: bool,
                 string: StringDdv):
        self._is_ignore_case = is_ignore_case
        self.string = string
        self.pattern = None

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return self.string.resolving_dependencies()

    def validate_pre_sds_if_applicable(self, hds: HomeDs) -> Optional[TextRenderer]:
        if self.pattern is None:
            if not self.string.resolving_dependencies():
                return self._compile_and_set_pattern(self.string.value_when_no_dir_dependencies())
        else:
            return None

    def validate_post_sds_if_applicable(self, tcds: TestCaseDs) -> Optional[TextRenderer]:
        if self.pattern is None:
            return self._compile_and_set_pattern(self.string.value_of_any_dependency(tcds))
        else:
            return None

    def pattern_when_no_dir_dependencies(self) -> Pattern:
        if self.pattern is None:
            self._compile_and_set_pattern(self.string.value_when_no_dir_dependencies())
        return self.pattern

    def pattern_of_any_dependency(self, tcds: TestCaseDs) -> Pattern:
        if self.pattern is None:
            self._compile_and_set_pattern(self.string.value_of_any_dependency(tcds))
        return self.pattern

    def _compile_and_set_pattern(self, regex_pattern: str) -> Optional[TextRenderer]:
        try:
            flags = 0
            if self._is_ignore_case:
                flags = re.IGNORECASE
            self.pattern = re.compile(regex_pattern, flags)
            return None
        except Exception as ex:
            return text_docs.single_line(
                str_constructor.FormatPositional(
                    "Invalid {}: '{}'",
                    syntax_elements.REGEX_SYNTAX_ELEMENT.singular_name,
                    ex,
                )
            )


class _RegexDdv(RegexDdv):
    def __init__(self,
                 is_ignore_case: bool,
                 string: StringDdv,
                 ):
        self._describer = custom_details.regex(
            is_ignore_case,
            details.String(string_rendering.AsToStringObject(string.describer()))
        )
        self._validator = _ValidatorWhichCreatesRegex(is_ignore_case, string)

    def describer(self) -> DetailsRenderer:
        return self._describer

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return self._validator.resolving_dependencies()

    def validator(self) -> DdvValidator:
        return self._validator

    def value_when_no_dir_dependencies(self) -> Pattern:
        return self._validator.pattern_when_no_dir_dependencies()

    def value_of_any_dependency(self, tcds: TestCaseDs) -> Pattern:
        return self._validator.pattern_of_any_dependency(tcds)
