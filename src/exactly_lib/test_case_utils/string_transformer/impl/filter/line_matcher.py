from typing import Iterator, Tuple

from exactly_lib.appl_env.app_env_dep_val import ApplicationEnvironmentDependentValue
from exactly_lib.appl_env.application_environment import ApplicationEnvironment
from exactly_lib.symbol.logic.string_transformer import StringTransformerSdv
from exactly_lib.tcfs.ddv_validation import DdvValidator
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.test_case_utils.description_tree.tree_structured import WithCachedTreeStructureDescriptionBase
from exactly_lib.test_case_utils.line_matcher import line_nums_interval
from exactly_lib.test_case_utils.line_matcher import model_construction
from exactly_lib.test_case_utils.string_transformer import sdvs
from exactly_lib.test_case_utils.string_transformer.impl.models.transformed_string_models import \
    StringTransformerFromLinesTransformer
from exactly_lib.type_system.description.tree_structured import StructureRenderer, WithTreeStructureDescription
from exactly_lib.type_system.logic.line_matcher import LineMatcher, LineMatcherAdv, LineMatcherDdv, \
    LineMatcherSdv, LineMatcherLine
from exactly_lib.type_system.logic.string_transformer import StringTransformerDdv, StringTransformer, \
    StringTransformerAdv
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
        return _FilterByLineMatcherDdvAdv(self._name, self._line_matcher.value_of_any_dependency(tcds))


class _FilterByLineMatcherDdvAdv(ApplicationEnvironmentDependentValue[StringTransformer]):
    def __init__(self,
                 name: str,
                 line_matcher: LineMatcherAdv,
                 ):
        self._name = name
        self._line_matcher = line_matcher

    def primitive(self, environment: ApplicationEnvironment) -> StringTransformer:
        return _FilterByLineMatcher(self._name, self._line_matcher.primitive(environment))


class _FilterByLineMatcher(WithCachedTreeStructureDescriptionBase, StringTransformerFromLinesTransformer):
    """
    Keeps lines matched by a given :class:`LineMatcher`,
    and discards lines not matched.
    """

    def __init__(self,
                 name: str,
                 line_matcher: LineMatcher,
                 ):
        super().__init__()
        self._name = name
        self._line_matcher = line_matcher

    @staticmethod
    def new_structure_tree(name: str, line_matcher: WithTreeStructureDescription) -> StructureRenderer:
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

    @property
    def line_matcher(self) -> LineMatcher:
        return self._line_matcher

    def _transformation_may_depend_on_external_resources(self) -> bool:
        return True

    def _transform(self, lines: Iterator[str]) -> Iterator[str]:
        return (
            line
            for line, line_matcher_model in self._line_and_line_matcher_models(lines)
            if self._line_matcher.matches_w_trace(line_matcher_model).value
        )

    def __str__(self):
        return '{}({})'.format(type(self).__name__,
                               str(self._line_matcher))

    def _line_and_line_matcher_models(self, lines: Iterator[str]) -> Iterator[Tuple[str, LineMatcherLine]]:
        line_nums_to_process = line_nums_interval.interval_of_matcher(self._line_matcher)
        return model_construction.original_and_model_iter_from_file_line_iter__interval(line_nums_to_process, lines)
