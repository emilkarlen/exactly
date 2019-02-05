from typing import Set, Pattern, Sequence

from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.entity import types
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.data.string_resolver import StringResolver
from exactly_lib.symbol.logic.string_transformer import StringTransformerResolver
from exactly_lib.symbol.object_with_symbol_references import references_from_objects_with_symbol_references
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.pre_or_post_value_validation import PreOrPostSdsValueValidator
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.test_case_utils.parse import parse_string
from exactly_lib.test_case_utils.regex import parse_regex
from exactly_lib.test_case_utils.regex.regex_value import RegexResolver, RegexValue
from exactly_lib.type_system.data.string_value import StringValue
from exactly_lib.type_system.logic.string_transformer import StringTransformer, StringTransformerModel
from exactly_lib.type_system.logic.string_transformer import StringTransformerValue
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.symbol_table import SymbolTable

REPLACE_REPLACEMENT_ARGUMENT = a.Named(types.STRING_TYPE_INFO.syntax_element_name)
_MISSING_REPLACEMENT_ARGUMENT_ERR_MSG = 'Missing ' + REPLACE_REPLACEMENT_ARGUMENT.name

_PARSE_REPLACEMENT_CONFIGURATION = parse_string.Configuration('REPLACEMENT')


def parse_replace(token_parser: TokenParser) -> StringTransformerResolver:
    token_parser.require_has_valid_head_token(syntax_elements.REGEX_SYNTAX_ELEMENT.singular_name)
    source_type, regex_resolver = parse_regex.parse_regex2(token_parser,
                                                           must_be_on_same_line=True)
    token_parser.require_is_not_at_eol(_MISSING_REPLACEMENT_ARGUMENT_ERR_MSG)

    replacement = parse_string.parse_string_from_token_parser(token_parser, _PARSE_REPLACEMENT_CONFIGURATION)

    return _Resolver(regex_resolver,
                     replacement)


class _Resolver(StringTransformerResolver):
    def __init__(self,
                 regex: RegexResolver,
                 replacement: StringResolver
                 ):
        self._regex = regex
        self._replacement = replacement
        self._references = references_from_objects_with_symbol_references([
            self._regex,
            self._replacement
        ])
        pass

    def resolve(self, symbols: SymbolTable) -> StringTransformerValue:
        return _Value(self._regex.resolve(symbols),
                      self._replacement.resolve(symbols))

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references


class _Value(StringTransformerValue):
    def __init__(self,
                 regex: RegexValue,
                 replacement: StringValue):
        self._regex = regex
        self._replacement = replacement
        self._resolving_dependencies = set(regex.resolving_dependencies())
        self._resolving_dependencies.update(replacement.resolving_dependencies())

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return self._resolving_dependencies

    def validator(self) -> PreOrPostSdsValueValidator:
        return self._regex.validator()

    def value_when_no_dir_dependencies(self) -> StringTransformer:
        return ReplaceStringTransformer(self._regex.value_when_no_dir_dependencies(),
                                        self._replacement.value_when_no_dir_dependencies())

    def value_of_any_dependency(self, home_and_sds: HomeAndSds) -> StringTransformer:
        return ReplaceStringTransformer(self._regex.value_of_any_dependency(home_and_sds),
                                        self._replacement.value_of_any_dependency(home_and_sds))


class ReplaceStringTransformer(StringTransformer):
    def __init__(self,
                 compiled_regular_expression: Pattern[str],
                 replacement: str):
        self._compiled_regular_expression = compiled_regular_expression
        self._replacement = replacement

    @property
    def regex_pattern_string(self) -> str:
        return self._compiled_regular_expression.pattern

    @property
    def replacement(self) -> str:
        return self._replacement

    def transform(self, lines: StringTransformerModel) -> StringTransformerModel:
        return (
            self._process_line(line)
            for line in lines
        )

    def _process_line(self, line: str) -> str:
        if line and line[-1] == '\n':
            return self._compiled_regular_expression.sub(self._replacement, line[:-1]) + '\n'
        else:
            return self._compiled_regular_expression.sub(self._replacement, line)

    def __str__(self):
        return '{}({})'.format(type(self).__name__,
                               str(self._compiled_regular_expression))
