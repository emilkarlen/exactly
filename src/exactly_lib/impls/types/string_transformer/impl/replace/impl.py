from typing import TypeVar, Generic, Pattern, Callable, Iterator, Optional, Sequence

from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.impls.description_tree import custom_details
from exactly_lib.impls.description_tree.tree_structured import WithCachedNodeDescriptionBase
from exactly_lib.impls.types.line_matcher import model_construction as _line_matcher_model_construction
from exactly_lib.impls.types.line_matcher.model_construction import FullContentsAndLineMatcherLine
from exactly_lib.impls.types.regex.regex_ddv import RegexSdv, RegexDdv
from exactly_lib.impls.types.string_transformer import names
from exactly_lib.impls.types.string_transformer.impl.sources.transformed_string_sources import \
    StringTransformerFromLinesTransformer
from exactly_lib.symbol.sdv_structure import references_from_objects_with_symbol_references, SymbolReference
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.test_case.app_env import ApplicationEnvironment
from exactly_lib.type_val_deps.dep_variants.adv.app_env_dep_val import ApplicationEnvironmentDependentValue
from exactly_lib.type_val_deps.dep_variants.ddv import ddv_validators
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import DdvValidator
from exactly_lib.type_val_deps.dep_variants.ddv.matcher import MatcherDdv
from exactly_lib.type_val_deps.dep_variants.sdv.full_deps.sdv import FullDepsSdv
from exactly_lib.type_val_deps.types.line_matcher import LineMatcherSdv, LineMatcherDdv, LineMatcherAdv
from exactly_lib.type_val_deps.types.string_.string_ddv import StringDdv
from exactly_lib.type_val_deps.types.string_.string_sdv import StringSdv
from exactly_lib.type_val_deps.types.string_transformer.ddv import StringTransformerDdv, StringTransformerAdv
from exactly_lib.type_val_deps.types.string_transformer.sdv import StringTransformerSdv
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer, WithNodeDescription
from exactly_lib.type_val_prims.matcher.line_matcher import LineMatcher
from exactly_lib.type_val_prims.string_transformer import StringTransformer
from exactly_lib.util import functional
from exactly_lib.util.description_tree import details, renderers
from exactly_lib.util.description_tree.renderer import NodeRenderer, DetailsRenderer
from exactly_lib.util.description_tree.tree import Node
from exactly_lib.util.render import strings
from exactly_lib.util.symbol_table import SymbolTable


class Sdv(StringTransformerSdv):
    def __init__(self,
                 lines_selector: Optional[LineMatcherSdv],
                 preserve_new_lines: bool,
                 regex: RegexSdv,
                 replacement: StringSdv,
                 ):
        self._lines_selector = lines_selector
        self._preserve_new_lines = preserve_new_lines
        self._regex = regex
        self._replacement = replacement
        self._references = references_from_objects_with_symbol_references(
            functional.filter_not_none([
                self._lines_selector,
                self._regex,
                self._replacement
            ]))

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def resolve(self, symbols: SymbolTable) -> StringTransformerDdv:
        return _Ddv(FullDepsSdv.resolve__optional(self._lines_selector, symbols),
                    self._preserve_new_lines,
                    self._regex.resolve(symbols),
                    self._replacement.resolve(symbols))


LINE = TypeVar('LINE')


class _Replacer(Generic[LINE]):
    def process(self, line: LINE) -> str:
        raise NotImplementedError('abstract method')


class _StrReplacer(_Replacer[str]):
    def __init__(self,
                 compiled_regular_expression: Pattern[str],
                 replacement: str,
                 ):
        self._regex = compiled_regular_expression
        self._replacement = replacement

    def process(self, line: str) -> str:
        raise NotImplementedError('abstract method')


class _StrReplacerIncludingNewLines(_StrReplacer):
    def process(self, line: str) -> str:
        return self._regex.sub(self._replacement, line)


class _StrReplacerExcludingNewLines(_StrReplacer):
    def process(self, line: str) -> str:
        if line[-1] == '\n':
            return self._regex.sub(self._replacement, line[:-1]) + '\n'
        else:
            return self._regex.sub(self._replacement, line)


class _ReplacerWLineMatcherSelector(_Replacer[FullContentsAndLineMatcherLine]):
    def __init__(self,
                 lines_selector: LineMatcher,
                 str_replacer: Callable[[str], str],
                 ):
        self.selector = lines_selector
        self.replacer = str_replacer

    def process(self, line: FullContentsAndLineMatcherLine) -> str:
        return (
            self.replacer(line[0])
            if self.selector.matches_w_trace(line[1]).value
            else
            line[0]
        )


class _ReplacerApplier:
    def may_depend_on_external_resources(self) -> bool:
        raise NotImplementedError('abstract method')

    def process(self, lines: Iterator[str]) -> Iterator[str]:
        raise NotImplementedError('abstract method')


class _ReplacerApplierWoLineMatcherSelector(_ReplacerApplier):
    def __init__(self, replacer: _StrReplacer):
        self._replacer = replacer

    def may_depend_on_external_resources(self) -> bool:
        return False

    def process(self, lines: Iterator[str]) -> Iterator[str]:
        return _lines_iterator_from_replacements(self._replacer.process, lines)


class _ReplacerApplierWLineMatcherSelector(_ReplacerApplier):
    def __init__(self,
                 lines_selector: LineMatcher,
                 replacer: _StrReplacer,
                 ):
        self._replacer = _ReplacerWLineMatcherSelector(lines_selector, replacer.process)

    def may_depend_on_external_resources(self) -> bool:
        return True

    def process(self, lines: Iterator[str]) -> Iterator[str]:
        return _lines_iterator_from_replacements(
            self._replacer.process,
            _line_matcher_model_construction.original_and_model_iter_from_file_line_iter(lines),
        )


def _lines_iterator_from_replacements(replacer: Callable[[LINE], str],
                                      lines: Iterator[LINE],
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


class _Ddv(StringTransformerDdv):
    def __init__(self,
                 lines_selector: Optional[LineMatcherDdv],
                 preserve_new_lines: bool,
                 regex: RegexDdv,
                 replacement: StringDdv,
                 ):
        self._lines_selector = lines_selector
        self._preserve_new_lines = preserve_new_lines
        self._regex = regex
        self._replacement = replacement

    def structure(self) -> StructureRenderer:
        return _StructureRendererForReplace(
            self._lines_selector,
            self._preserve_new_lines,
            self._regex.describer(),
            details.String(strings.AsToStringObject(self._replacement.describer())),
        )

    @property
    def validator(self) -> DdvValidator:
        return (
            self._regex.validator()
            if self._lines_selector is None
            else
            ddv_validators.all_of([
                self._lines_selector.validator,
                self._regex.validator(),
            ])
        )

    def value_of_any_dependency(self, tcds: TestCaseDs) -> StringTransformerAdv:
        return _Adv(MatcherDdv.value_of_any_dependency__optional(self._lines_selector, tcds),
                    self._preserve_new_lines,
                    self._regex.value_of_any_dependency(tcds),
                    self._replacement.value_of_any_dependency(tcds))


class _Adv(ApplicationEnvironmentDependentValue[StringTransformer]):
    def __init__(self,
                 lines_selector: Optional[LineMatcherAdv],
                 preserve_new_lines: bool,
                 regex: Pattern,
                 replacement: str,
                 ):
        self._lines_selector = lines_selector
        self._preserve_new_lines = preserve_new_lines
        self._regex = regex
        self._replacement = replacement

    def primitive(self, environment: ApplicationEnvironment) -> StringTransformer:
        return _ReplaceStringTransformer(
            ApplicationEnvironmentDependentValue.primitive__optional(self._lines_selector,
                                                                     environment),
            self._preserve_new_lines,
            self._regex,
            self._replacement)


class _StructureRendererForReplace(NodeRenderer[None]):
    _PATTERN_HEADER = 'pattern ' + syntax_elements.REGEX_SYNTAX_ELEMENT.singular_name
    _REPLACEMENT_HEADER = 'replacement ' + syntax_elements.STRING_SYNTAX_ELEMENT.singular_name
    _LINES_SELECTOR_HEADER = 'replacement ' + syntax_elements.STRING_SYNTAX_ELEMENT.singular_name

    def __init__(self,
                 lines_selector: Optional[WithNodeDescription],
                 preserve_new_lines: bool,
                 pattern: DetailsRenderer,
                 replacement: DetailsRenderer):
        self._line_matcher = lines_selector
        self._preserve_new_lines = preserve_new_lines
        self._pattern = pattern
        self._replacement = replacement

    def render(self) -> Node[None]:
        return self._renderer().render()

    def _renderer(self) -> StructureRenderer:
        return renderers.NodeRendererFromParts(
            names.REPLACE_TRANSFORMER_NAME,
            None,
            (
                self._lines_selection_renderer(),
                custom_details.optional_option(names.PRESERVE_NEW_LINES_OPTION_NAME, self._preserve_new_lines),
                details.HeaderAndValue(self._PATTERN_HEADER,
                                       self._pattern),
                details.HeaderAndValue(self._REPLACEMENT_HEADER,
                                       self._replacement),
            ),
            (),
        )

    def _lines_selection_renderer(self) -> DetailsRenderer:
        if self._line_matcher is None:
            return details.empty()
        else:
            return custom_details.HeaderAndValue(
                custom_details.option_str(names.LINES_SELECTION_OPTION),
                custom_details.WithTreeStructure(self._line_matcher),
            )


class _ReplaceStringTransformer(WithCachedNodeDescriptionBase, StringTransformerFromLinesTransformer):
    _PATTERN_HEADER = 'pattern ' + syntax_elements.REGEX_SYNTAX_ELEMENT.singular_name
    _REPLACEMENT_HEADER = 'replacement ' + syntax_elements.STRING_SYNTAX_ELEMENT.singular_name

    def __init__(self,
                 lines_selector: Optional[LineMatcher],
                 preserve_new_lines: bool,
                 compiled_regular_expression: Pattern[str],
                 replacement: str,
                 ):
        super().__init__()
        str_replacer = (
            _StrReplacerExcludingNewLines(compiled_regular_expression,
                                          replacement)
            if preserve_new_lines
            else
            _StrReplacerIncludingNewLines(compiled_regular_expression,
                                          replacement)
        )
        self._replacer_applier = (
            _ReplacerApplierWoLineMatcherSelector(str_replacer)
            if lines_selector is None
            else
            _ReplacerApplierWLineMatcherSelector(lines_selector, str_replacer)
        )
        self._structure_renderer = _StructureRendererForReplace(
            lines_selector,
            preserve_new_lines,
            custom_details.PatternRenderer(compiled_regular_expression),
            details.String(replacement),
        )

    @property
    def name(self) -> str:
        return names.REPLACE_TRANSFORMER_NAME

    def _structure(self) -> StructureRenderer:
        return self._structure_renderer

    def _transformation_may_depend_on_external_resources(self) -> bool:
        return self._replacer_applier.may_depend_on_external_resources()

    def _transform(self, lines: Iterator[str]) -> Iterator[str]:
        return self._replacer_applier.process(lines)
