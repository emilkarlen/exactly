from abc import ABC, abstractmethod
from pathlib import PurePath
from typing import Callable, Sequence

from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.impls.description_tree import custom_details
from exactly_lib.impls.types.files_matcher import config
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.test_case.app_env import ApplicationEnvironment
from exactly_lib.type_val_deps.dep_variants.adv.matcher import MatcherAdv
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import DdvValidator
from exactly_lib.type_val_deps.dep_variants.ddv.matcher import MatcherDdv
from exactly_lib.type_val_deps.types.files_condition.ddv import FilesConditionAdv, FilesCondition, FilesConditionDdv
from exactly_lib.type_val_deps.types.files_condition.sdv import FilesConditionSdv
from exactly_lib.type_val_deps.types.files_matcher import FilesMatcherAdv, FilesMatcherDdv
from exactly_lib.type_val_deps.types.matcher import MatcherSdv
from exactly_lib.type_val_prims.description.trace_building import TraceBuilder
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.type_val_prims.matcher.files_matcher import FilesMatcherModel, FilesMatcher
from exactly_lib.type_val_prims.matcher.matcher_base_class import MatcherWTrace
from exactly_lib.type_val_prims.matcher.matching_result import MatchingResult
from exactly_lib.util.cli_syntax import option_syntax
from exactly_lib.util.description_tree import renderers, details
from exactly_lib.util.description_tree.renderer import DetailsRenderer, NodeRenderer
from exactly_lib.util.description_tree.tree import Node
from exactly_lib.util.symbol_table import SymbolTable

NUM_FILES_LESS = 'Too few files'
NO_FILES__ACTUAL = '0 files'
NUM_FILES_MORE = 'Too many files'
UNEXPECTED_NAME = 'File with unexpected name'
NON_MATCHING_MATCHER = ('File that does not match corresponding ' +
                        syntax_elements.FILE_MATCHER_SYNTAX_ELEMENT.singular_name)

FILES_FOUND = 'Found files'
FILES_NOT_FOUND = 'Not found files'


class Applier(ABC):
    def __init__(self,
                 name: str,
                 files_condition: FilesCondition,
                 model: FilesMatcherModel,
                 ):
        self.name = name
        self.model = model
        self.files_condition = files_condition

    @abstractmethod
    def apply(self) -> MatchingResult:
        pass

    def _result_true(self) -> MatchingResult:
        return (
            TraceBuilder(self.name)
                .append_details(self.files_condition.describer)
                .build_result(True)
        )


class Conf:
    def __init__(self,
                 name: str,
                 make_matcher: Callable[[str, FilesCondition, FilesMatcherModel], Applier],
                 ):
        self.name = name
        self.applier_for_model = make_matcher


class RendererOfNonMatchingFileMatcher(NodeRenderer[bool]):
    def __init__(self,
                 name: str,
                 non_matching_path: PurePath,
                 non_match_result: MatchingResult,
                 ):
        self._name = name
        self._non_matching_path = non_matching_path
        self._non_match_result = non_match_result

    def render(self) -> Node[bool]:
        file_spec_renderer = custom_details.HeaderAndValue(
            NON_MATCHING_MATCHER,
            details.String(self._non_matching_path)
        )
        return Node(self._name,
                    False,
                    file_spec_renderer.render(),
                    (self._non_match_result.trace.render(),)
                    )


class _Matcher(MatcherWTrace[FilesMatcherModel]):
    def __init__(self,
                 conf: Conf,
                 files_condition: FilesCondition,
                 ):
        self._conf = conf
        self._files_condition = files_condition
        self._structure = self.new_structure_tree(conf.name, files_condition.describer)

    @staticmethod
    def new_structure_tree(name: str, files_condition: DetailsRenderer) -> StructureRenderer:
        return renderers.header_and_detail(name, files_condition)

    @property
    def name(self) -> str:
        return self._conf.name

    def structure(self) -> StructureRenderer:
        return self._structure

    def matches_w_trace(self, model: FilesMatcherModel) -> MatchingResult:
        applier = self._conf.applier_for_model(self._conf.name,
                                               self._files_condition,
                                               model)
        return applier.apply()


class _MatcherAdv(MatcherAdv[FilesMatcherModel]):
    def __init__(self,
                 conf: Conf,
                 files_condition: FilesConditionAdv,
                 ):
        self._conf = conf
        self._files_condition = files_condition

    def primitive(self, environment: ApplicationEnvironment) -> FilesMatcher:
        return _Matcher(self._conf,
                        self._files_condition.primitive(environment))


class _MatcherDdv(MatcherDdv[FilesMatcherModel]):
    def __init__(self,
                 conf: Conf,
                 files_condition: FilesConditionDdv,
                 ):
        self._conf = conf
        self._files_condition = files_condition

    def structure(self) -> StructureRenderer:
        return _Matcher.new_structure_tree(self._conf.name,
                                           self._files_condition.describer)

    @property
    def validator(self) -> DdvValidator:
        return self._files_condition.validator

    def value_of_any_dependency(self, tcds: TestCaseDs) -> FilesMatcherAdv:
        return _MatcherAdv(self._conf,
                           self._files_condition.value_of_any_dependency(tcds))


class MatcherSdvWithApplier(MatcherSdv[FilesMatcherModel]):
    def __init__(self,
                 conf: Conf,
                 files_condition: FilesConditionSdv,
                 ):
        self._conf = conf
        self._files_condition = files_condition

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._files_condition.references

    def resolve(self, symbols: SymbolTable) -> FilesMatcherDdv:
        return _MatcherDdv(self._conf,
                           self._files_condition.resolve(symbols))


def _structure_name(full: bool) -> str:
    elements = [
        config.MATCHES_ARGUMENT,
        syntax_elements.FILES_CONDITION_SYNTAX_ELEMENT.singular_name,
    ]
    if full:
        elements.insert(1, option_syntax.option_syntax(config.MATCHES_FULL_OPTION.name))
    return ' '.join(elements)


MATCHES_FULL__STRUCTURE_NAME = _structure_name(True)
MATCHES_NON_FULL__STRUCTURE_NAME = _structure_name(False)
