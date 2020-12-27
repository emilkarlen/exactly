from typing import Iterator, Tuple

from exactly_lib.impls.description_tree.tree_structured import WithCachedNodeDescriptionBase
from exactly_lib.impls.types.line_matcher import line_nums_interval
from exactly_lib.impls.types.line_matcher import model_construction
from exactly_lib.impls.types.string_source import cached_frozen
from exactly_lib.impls.types.string_transformer import sdvs
from exactly_lib.impls.types.string_transformer.impl.filter.string_sources import \
    TransformedContentsViaAsLinesBase
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.type_val_deps.dep_variants.adv.app_env_dep_val import ApplicationEnvironment, \
    ApplicationEnvironmentDependentValue
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import DdvValidator
from exactly_lib.type_val_deps.types.line_matcher import LineMatcherAdv, LineMatcherDdv, LineMatcherSdv
from exactly_lib.type_val_deps.types.string_transformer.ddv import StringTransformerAdv, StringTransformerDdv
from exactly_lib.type_val_deps.types.string_transformer.sdv import StringTransformerSdv
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer, WithNodeDescription
from exactly_lib.type_val_prims.matcher.line_matcher import LineMatcher, LineMatcherLine
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.type_val_prims.string_source.structure_builder import StringSourceStructureBuilder
from exactly_lib.type_val_prims.string_transformer import StringTransformer
from exactly_lib.util.description_tree import renderers
from exactly_lib.util.symbol_table import SymbolTable


def sdv(name: str, line_matcher: LineMatcherSdv) -> StringTransformerSdv:
    def make_ddv(symbols: SymbolTable) -> StringTransformerDdv:
        return _FilterByLineMatcherDdv(name, line_matcher.resolve(symbols))

    return sdvs.SdvFromParts(
        make_ddv,
        line_matcher.references,
    )


class _FilterByLineMatcherDdv(StringTransformerDdv):
    """
    Keeps lines matched by a given Line Matcher
    and discards lines not matched.
    """

    def __init__(self,
                 name: str,
                 line_matcher: LineMatcherDdv,
                 ):
        self._name = name
        self._line_matcher = line_matcher

    def structure(self) -> StructureRenderer:
        return _FilterByLineMatcher.new_structure_tree(self._name, self._line_matcher)

    @property
    def validator(self) -> DdvValidator:
        return self._line_matcher.validator

    def value_of_any_dependency(self, tcds: TestCaseDs) -> StringTransformerAdv:
        return _FilterByLineMatcherAdv(self._name, self._line_matcher.value_of_any_dependency(tcds))


class _FilterByLineMatcherAdv(ApplicationEnvironmentDependentValue[StringTransformer]):
    def __init__(self,
                 name: str,
                 line_matcher: LineMatcherAdv,
                 ):
        self._name = name
        self._line_matcher = line_matcher

    def primitive(self, environment: ApplicationEnvironment) -> StringTransformer:
        return _FilterByLineMatcher(self._name,
                                    self._line_matcher.primitive(environment),
                                    environment.mem_buff_size,
                                    )


class _FilterByLineMatcher(WithCachedNodeDescriptionBase, StringTransformer):
    """
    Keeps lines matched by a given :class:`LineMatcher`,
    and discards lines not matched.
    """

    def __init__(self,
                 name: str,
                 line_matcher: LineMatcher,
                 mem_buff_size: int,
                 ):
        WithCachedNodeDescriptionBase.__init__(self)
        self._name = name
        self._line_matcher = line_matcher
        self._mem_buff_size = mem_buff_size

    @staticmethod
    def new_structure_tree(name: str, line_matcher: WithNodeDescription) -> StructureRenderer:
        return renderers.NodeRendererFromParts(
            name,
            None,
            (),
            (line_matcher.structure(),),
        )

    @property
    def name(self) -> str:
        return self._name

    def _structure(self) -> StructureRenderer:
        return self.new_structure_tree(self._name, self._line_matcher)

    def transform(self, model: StringSource) -> StringSource:
        def new_structure_builder() -> StringSourceStructureBuilder:
            return model.new_structure_builder().with_transformed_by(self.structure())

        return cached_frozen.StringSourceWithCachedFrozen(
            new_structure_builder,
            _ContentsViaAsLines(self._line_matcher, model, self._name),
            self._mem_buff_size,
            None,
        )


class _ContentsViaAsLines(TransformedContentsViaAsLinesBase):
    def __init__(self,
                 line_matcher: LineMatcher,
                 source: StringSource,
                 file_name: str,
                 ):
        super().__init__(source, file_name)
        self._line_matcher = line_matcher

    @property
    def may_depend_on_external_resources(self) -> bool:
        return True

    def _transform_lines(self, lines: Iterator[str]) -> Iterator[str]:
        return (
            line
            for line, line_matcher_model in self._line_and_line_matcher_models(lines)
            if self._line_matcher.matches_w_trace(line_matcher_model).value
        )

    def _line_and_line_matcher_models(self, lines: Iterator[str]) -> Iterator[Tuple[str, LineMatcherLine]]:
        line_nums_to_process = line_nums_interval.interval_of_matcher(self._line_matcher)
        return model_construction.original_and_model_iter_from_file_line_iter__interval(line_nums_to_process, lines)
