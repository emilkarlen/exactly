from typing import Pattern, Sequence, Iterator, Callable

from exactly_lib.common.help import headers
from exactly_lib.definitions import formatting, misc_texts
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.entity import types
from exactly_lib.impls.description_tree import custom_details
from exactly_lib.impls.description_tree.tree_structured import WithCachedNodeDescriptionBase
from exactly_lib.impls.types.expression import grammar
from exactly_lib.impls.types.regex import parse_regex
from exactly_lib.impls.types.regex.regex_ddv import RegexSdv, RegexDdv
from exactly_lib.impls.types.string_ import parse_string
from exactly_lib.impls.types.string_transformer import names
from exactly_lib.impls.types.string_transformer.impl.sources.transformed_string_sources import \
    StringTransformerFromLinesTransformer
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.sdv_structure import SymbolReference, references_from_objects_with_symbol_references
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.type_val_deps.dep_variants.adv.app_env_dep_val import ApplicationEnvironment, \
    ApplicationEnvironmentDependentValue
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import DdvValidator
from exactly_lib.type_val_deps.types.string_.string_ddv import StringDdv
from exactly_lib.type_val_deps.types.string_.string_sdv import StringSdv
from exactly_lib.type_val_deps.types.string_transformer.ddv import StringTransformerAdv, StringTransformerDdv
from exactly_lib.type_val_deps.types.string_transformer.sdv import StringTransformerSdv
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.type_val_prims.string_transformer import StringTransformer
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
    preserve_new_lines = token_parser.consume_optional_option(names.PRESERVE_NEW_LINES_OPTION_NAME)
    regex_sdv = parse_regex.parse_regex2(token_parser,
                                         must_be_on_same_line=True)
    token_parser.require_is_not_at_eol(_MISSING_REPLACEMENT_ARGUMENT_ERR_MSG)

    replacement = parse_string.parse_string_from_token_parser(token_parser, _PARSE_REPLACEMENT_CONFIGURATION)

    return _Sdv(preserve_new_lines,
                regex_sdv,
                replacement)


class _Sdv(StringTransformerSdv):
    def __init__(self,
                 preserve_new_lines: bool,
                 regex: RegexSdv,
                 replacement: StringSdv,
                 ):
        self._preserve_new_lines = preserve_new_lines
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
        return _Ddv(self._preserve_new_lines,
                    self._regex.resolve(symbols),
                    self._replacement.resolve(symbols))


class _Adv(ApplicationEnvironmentDependentValue[StringTransformer]):
    def __init__(self,
                 preserve_new_lines: bool,
                 regex: Pattern,
                 replacement: str,
                 ):
        self._preserve_new_lines = preserve_new_lines
        self._regex = regex
        self._replacement = replacement

    def primitive(self, environment: ApplicationEnvironment) -> StringTransformer:
        return _ReplaceStringTransformer(self._preserve_new_lines,
                                         self._regex,
                                         self._replacement)


class _Ddv(StringTransformerDdv):
    def __init__(self,
                 preserve_new_lines: bool,
                 regex: RegexDdv,
                 replacement: StringDdv,
                 ):
        self._preserve_new_lines = preserve_new_lines
        self._regex = regex
        self._replacement = replacement

    def structure(self) -> StructureRenderer:
        return _ReplaceStringTransformer.new_structure_tree(
            self._preserve_new_lines,
            self._regex.describer(),
            details.String(strings.AsToStringObject(self._replacement.describer())),
        )

    @property
    def validator(self) -> DdvValidator:
        return self._regex.validator()

    def value_of_any_dependency(self, tcds: TestCaseDs) -> StringTransformerAdv:
        return _Adv(self._preserve_new_lines,
                    self._regex.value_of_any_dependency(tcds),
                    self._replacement.value_of_any_dependency(tcds))


class _ReplaceStringTransformer(WithCachedNodeDescriptionBase, StringTransformerFromLinesTransformer):
    _PATTERN_HEADER = 'pattern ' + syntax_elements.REGEX_SYNTAX_ELEMENT.singular_name
    _REPLACEMENT_HEADER = 'replacement ' + syntax_elements.STRING_SYNTAX_ELEMENT.singular_name

    def __init__(self,
                 preserve_new_lines: bool,
                 compiled_regular_expression: Pattern[str],
                 replacement: str,
                 ):
        super().__init__()
        self._preserve_new_lines = preserve_new_lines
        self._compiled_regex = compiled_regular_expression
        self._replacement = replacement

    @staticmethod
    def new_structure_tree(preserve_new_lines: bool,
                           pattern: DetailsRenderer,
                           replacement: DetailsRenderer) -> StructureRenderer:
        return renderers.NodeRendererFromParts(
            names.REPLACE_TRANSFORMER_NAME,
            None,
            (
                custom_details.optional_option(names.PRESERVE_NEW_LINES_OPTION_NAME, preserve_new_lines),
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
            self._preserve_new_lines,
            custom_details.PatternRenderer(self._compiled_regex),
            details.String(self._replacement),
        )

    @property
    def regex_pattern_string(self) -> str:
        return self._compiled_regex.pattern

    @property
    def replacement(self) -> str:
        return self._replacement

    def _transformation_may_depend_on_external_resources(self) -> bool:
        return False

    def _transform(self, lines: Iterator[str]) -> Iterator[str]:
        return (
            self._iterator(self._replace_excluding_new_lines, lines)
            if self._preserve_new_lines
            else
            self._iterator(self._replace_including_new_lines, lines)
        )

    @staticmethod
    def _iterator(replacer: Callable[[str], str],
                  lines: Iterator[str],
                  ) -> Iterator[str]:
        segments = []
        for line in lines:
            sub_l = replacer(line)
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

    def _replace_including_new_lines(self, line: str) -> str:
        return self._compiled_regex.sub(self._replacement, line)

    def _replace_excluding_new_lines(self, line: str) -> str:
        if line[-1] == '\n':
            return self._replace_including_new_lines(line[:-1]) + '\n'
        else:
            return self._replace_including_new_lines(line)

    def __str__(self):
        return '{}({})'.format(type(self).__name__,
                               str(self._compiled_regex))


class SyntaxDescription(grammar.PrimitiveDescriptionWithNameAsInitialSyntaxToken):
    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        return [
            a.Single(a.Multiplicity.OPTIONAL,
                     names.PRESERVE_NEW_LINES_OPTION),
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
    'preserve_new_lines_option': formatting.argument_option(names.PRESERVE_NEW_LINES_OPTION_NAME),
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


Every line ends with {NL},
except the last line, which may or may not end with {NL}.

If {preserve_new_lines_option} is given,
this {NL} is excluded from the replacement.


{Note}
{LINES_ARE_SEPARATED_BY_NEW_LINE}
"""
