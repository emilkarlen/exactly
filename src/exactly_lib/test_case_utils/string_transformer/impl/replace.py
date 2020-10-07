from typing import Pattern, Sequence, Iterator

from exactly_lib.common.help import headers
from exactly_lib.definitions import formatting, misc_texts
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.entity import types
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.data.string_sdv import StringSdv
from exactly_lib.symbol.logic.string_transformer import StringTransformerSdv
from exactly_lib.symbol.sdv_structure import SymbolReference, references_from_objects_with_symbol_references
from exactly_lib.tcfs.ddv_validation import DdvValidator
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.test_case_utils.description_tree import custom_details
from exactly_lib.test_case_utils.description_tree.tree_structured import WithCachedTreeStructureDescriptionBase
from exactly_lib.test_case_utils.expression import grammar
from exactly_lib.test_case_utils.parse import parse_string
from exactly_lib.test_case_utils.regex import parse_regex
from exactly_lib.test_case_utils.regex.regex_ddv import RegexSdv, RegexDdv
from exactly_lib.test_case_utils.string_transformer import names
from exactly_lib.test_case_utils.string_transformer.impl.models.transformed_string_models import \
    StringTransformerFromLinesTransformer
from exactly_lib.type_system.data.string_ddv import StringDdv
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.application_environment import ApplicationEnvironment
from exactly_lib.type_system.logic.logic_base_class import ApplicationEnvironmentDependentValue
from exactly_lib.type_system.logic.string_transformer import StringTransformer, StringTransformerAdv
from exactly_lib.type_system.logic.string_transformer import StringTransformerDdv
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.description_tree import renderers, details
from exactly_lib.util.description_tree.renderer import DetailsRenderer
from exactly_lib.util.render import strings
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser

REPLACE_REGEX_ARGUMENT = syntax_elements.REGEX_SYNTAX_ELEMENT.argument

REPLACE_REPLACEMENT_ARGUMENT = a.Named(types.STRING_TYPE_INFO.syntax_element_name)
_MISSING_REPLACEMENT_ARGUMENT_ERR_MSG = 'Missing ' + REPLACE_REPLACEMENT_ARGUMENT.name

_PARSE_REPLACEMENT_CONFIGURATION = parse_string.Configuration('REPLACEMENT')


def parse_replace(token_parser: TokenParser) -> StringTransformerSdv:
    token_parser.require_has_valid_head_token(REPLACE_REGEX_ARGUMENT.name)
    source_type, regex_sdv = parse_regex.parse_regex2(token_parser,
                                                      must_be_on_same_line=True)
    token_parser.require_is_not_at_eol(_MISSING_REPLACEMENT_ARGUMENT_ERR_MSG)

    replacement = parse_string.parse_string_from_token_parser(token_parser, _PARSE_REPLACEMENT_CONFIGURATION)

    return _Sdv(regex_sdv,
                replacement)


class _Sdv(StringTransformerSdv):
    def __init__(self,
                 regex: RegexSdv,
                 replacement: StringSdv
                 ):
        self._regex = regex
        self._replacement = replacement
        self._references = references_from_objects_with_symbol_references([
            self._regex,
            self._replacement
        ])

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def resolve(self, symbols: SymbolTable) -> StringTransformerDdv:
        return _Ddv(self._regex.resolve(symbols),
                    self._replacement.resolve(symbols))


class _Adv(ApplicationEnvironmentDependentValue[StringTransformer]):
    def __init__(self,
                 regex: Pattern,
                 replacement: str):
        self._regex = regex
        self._replacement = replacement

    def primitive(self, environment: ApplicationEnvironment) -> StringTransformer:
        return _ReplaceStringTransformer(self._regex,
                                         self._replacement)


class _Ddv(StringTransformerDdv):
    def __init__(self,
                 regex: RegexDdv,
                 replacement: StringDdv):
        self._regex = regex
        self._replacement = replacement

    def structure(self) -> StructureRenderer:
        return _ReplaceStringTransformer.new_structure_tree(
            self._regex.describer(),
            details.String(strings.AsToStringObject(self._replacement.describer())),
        )

    @property
    def validator(self) -> DdvValidator:
        return self._regex.validator()

    def value_of_any_dependency(self, tcds: TestCaseDs) -> StringTransformerAdv:
        return _Adv(self._regex.value_of_any_dependency(tcds),
                    self._replacement.value_of_any_dependency(tcds))


class _ReplaceStringTransformer(WithCachedTreeStructureDescriptionBase, StringTransformerFromLinesTransformer):
    _PATTERN_HEADER = 'pattern ' + syntax_elements.REGEX_SYNTAX_ELEMENT.singular_name
    _REPLACEMENT_HEADER = 'replacement ' + syntax_elements.STRING_SYNTAX_ELEMENT.singular_name

    def __init__(self,
                 compiled_regular_expression: Pattern[str],
                 replacement: str):
        super().__init__()
        self._compiled_regular_expression = compiled_regular_expression
        self._replacement = replacement

    @staticmethod
    def new_structure_tree(pattern: DetailsRenderer,
                           replacement: DetailsRenderer) -> StructureRenderer:
        return renderers.NodeRendererFromParts(
            names.REPLACE_TRANSFORMER_NAME,
            None,
            (
                details.HeaderAndValue(_ReplaceStringTransformer._PATTERN_HEADER,
                                       pattern),
                details.HeaderAndValue(_ReplaceStringTransformer._REPLACEMENT_HEADER,
                                       replacement),
            ),
            (),
        )

    @property
    def name(self) -> str:
        return names.REPLACE_TRANSFORMER_NAME

    def _structure(self) -> StructureRenderer:
        return self.new_structure_tree(
            custom_details.PatternRenderer(self._compiled_regular_expression),
            details.String(self._replacement),
        )

    @property
    def regex_pattern_string(self) -> str:
        return self._compiled_regular_expression.pattern

    @property
    def replacement(self) -> str:
        return self._replacement

    def _transform(self, lines: Iterator[str]) -> Iterator[str]:
        re = self._compiled_regular_expression
        replacement = self._replacement

        segments = []
        for line in lines:
            sub_l = re.sub(replacement, line)
            nli = sub_l.find('\n')
            while nli != -1:
                segments.append(sub_l[:nli + 1])
                yield ''.join(segments)
                segments = []
                sub_l = sub_l[nli + 1:]
                nli = sub_l.find('\n')
            if sub_l != '':
                segments.append(sub_l)
        rest = ''.join(segments)
        if rest != '':
            yield rest

    def __str__(self):
        return '{}({})'.format(type(self).__name__,
                               str(self._compiled_regular_expression))


class SyntaxDescription(grammar.PrimitiveDescriptionWithNameAsInitialSyntaxToken):
    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        return [
            a.Single(a.Multiplicity.MANDATORY,
                     REPLACE_REGEX_ARGUMENT),
            a.Single(a.Multiplicity.MANDATORY,
                     REPLACE_REPLACEMENT_ARGUMENT),
        ]

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        return _TEXT_PARSER.fnap(_REPLACE_TRANSFORMER_SED_DESCRIPTION)

    @property
    def see_also_targets(self) -> Sequence[SeeAlsoTarget]:
        return [syntax_elements.REGEX_SYNTAX_ELEMENT.cross_reference_target]


_TEXT_PARSER = TextParser({
    '_REG_EX_': REPLACE_REGEX_ARGUMENT.name,
    '_STRING_': REPLACE_REPLACEMENT_ARGUMENT.name,
    'Note': headers.NOTE_LINE_HEADER,
    'NL': formatting.string_constant('\\n'),
    'LINES_ARE_SEPARATED_BY_NEW_LINE': misc_texts.LINES_ARE_SEPARATED_BY_NEW_LINE,
})

_REPLACE_TRANSFORMER_SED_DESCRIPTION = """\
Replaces every string matching {_REG_EX_} (on a single line) with {_STRING_}.


Backslash escapes in {_STRING_} are processed.
That is, \\n is converted to a single newline character, \\r is converted to a carriage return, and so forth.


Unknown escapes such as \\& are left alone.


Back-references, such as \\6, are replaced with the substring matched by group 6 in {_REG_EX_}.


{Note}
{LINES_ARE_SEPARATED_BY_NEW_LINE}


{Note}
Every line ends with {NL},
except the last line, which may or may not end with {NL}.
"""
