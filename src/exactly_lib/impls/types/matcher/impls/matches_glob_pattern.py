import fnmatch
from pathlib import Path
from typing import Callable

from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.primitives import str_matcher
from exactly_lib.impls.description_tree import custom_details
from exactly_lib.impls.description_tree.tree_structured import WithCachedNodeDescriptionBase
from exactly_lib.impls.types.matcher.impls import sdv_components
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.type_val_deps.dep_variants.adv import advs
from exactly_lib.type_val_deps.dep_variants.adv.matcher import MatcherAdv
from exactly_lib.type_val_deps.dep_variants.ddv.matcher import MatcherDdv
from exactly_lib.type_val_deps.types.file_matcher import FileMatcherDdv
from exactly_lib.type_val_deps.types.matcher import MatcherSdv
from exactly_lib.type_val_deps.types.string_.string_ddv import StringDdv
from exactly_lib.type_val_deps.types.string_.string_sdv import StringSdv
from exactly_lib.type_val_prims.description.trace_building import TraceBuilder
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.type_val_prims.matcher.matcher_base_class import MODEL, MatcherWTrace
from exactly_lib.type_val_prims.matcher.matching_result import MatchingResult
from exactly_lib.util.description_tree import details, renderers
from exactly_lib.util.description_tree.renderer import DetailsRenderer
from exactly_lib.util.render import strings as string_rendering
from exactly_lib.util.str_ import str_constructor
from exactly_lib.util.symbol_table import SymbolTable


def sdv__path(glob_pattern: StringSdv) -> MatcherSdv[Path]:
    def make_ddv(symbols: SymbolTable) -> FileMatcherDdv:
        return MatchesGlobPatternDdv(_match_path, glob_pattern.resolve(symbols))

    return sdv_components.MatcherSdvFromParts(
        glob_pattern.references,
        make_ddv,
    )


def sdv__str(glob_pattern: StringSdv) -> MatcherSdv[str]:
    def make_ddv(symbols: SymbolTable) -> FileMatcherDdv:
        return MatchesGlobPatternDdv(_match_str, glob_pattern.resolve(symbols))

    return sdv_components.MatcherSdvFromParts(
        glob_pattern.references,
        make_ddv,
    )


def _match_path(model: Path, pattern: str) -> bool:
    return model.match(pattern)


def _match_str(model: str, pattern: str) -> bool:
    return fnmatch.fnmatch(model, pattern)


class MatchesGlobPatternDdv(MatcherDdv[MODEL]):
    def __init__(self,
                 matcher: Callable[[MODEL, str], bool],
                 glob_pattern: StringDdv,
                 ):
        self._matcher = matcher
        self._glob_pattern = glob_pattern

    def structure(self) -> StructureRenderer:
        return MatchesGlobPattern.new_structure_tree(
            details.String(str_constructor.Repr(string_rendering.AsToStringObject(self._glob_pattern.describer())))
        )

    def value_of_any_dependency(self, tcds: TestCaseDs) -> MatcherAdv[MODEL]:
        return advs.ConstantMatcherAdv(
            MatchesGlobPattern(self._matcher,
                               self._glob_pattern.value_of_any_dependency(tcds),
                               )
        )


class MatchesGlobPattern(WithCachedNodeDescriptionBase,
                         MatcherWTrace[MODEL]
                         ):
    NAME = ' '.join((
        str_matcher.MATCH_REGEX_ARGUMENT,
        syntax_elements.GLOB_PATTERN_SYNTAX_ELEMENT.singular_name,
    ))

    def __init__(self,
                 matcher: Callable[[MODEL, str], bool],
                 glob_pattern: str,
                 ):
        super().__init__()
        self._matcher = matcher
        self._glob_pattern = glob_pattern
        self._renderer_of_expected = custom_details.expected(
            details.String(str_constructor.Repr(glob_pattern))
        )

    @property
    def name(self) -> str:
        return self.NAME

    @staticmethod
    def new_structure_tree(glob_pattern: DetailsRenderer) -> StructureRenderer:
        return renderers.NodeRendererFromParts(
            MatchesGlobPattern.NAME,
            None,
            (glob_pattern,),
            (),
        )

    def _structure(self) -> StructureRenderer:
        return self.new_structure_tree(
            details.String(str_constructor.Repr(self._glob_pattern))
        )

    def matches_w_trace(self, model: MODEL) -> MatchingResult:
        tb = self._new_tb_with_expected().append_details(
            custom_details.actual(
                details.String(str_constructor.Repr(str(model)))
            )
        )
        return tb.build_result(self._matcher(model, self._glob_pattern))

    def _new_tb_with_expected(self) -> TraceBuilder:
        return TraceBuilder(self.NAME).append_details(self._renderer_of_expected)
