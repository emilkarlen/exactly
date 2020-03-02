from abc import ABC, abstractmethod
from typing import Callable, Sequence

from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.symbol.logic.matcher import MatcherSdv
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.test_case_file_structure.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.files_condition.structure import FilesCondition, FilesConditionAdv, FilesConditionDdv, \
    FilesConditionSdv
from exactly_lib.test_case_utils.files_matcher import config
from exactly_lib.test_case_utils.matcher.impls import combinator_matchers
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.files_matcher import FilesMatcherModel, FilesMatcher, FilesMatcherAdv, \
    FilesMatcherDdv
from exactly_lib.type_system.logic.logic_base_class import ApplicationEnvironment
from exactly_lib.type_system.logic.matcher_base_class import MatcherWTraceAndNegation, MatcherAdv, MatcherDdv, \
    MatchingResult
from exactly_lib.util.description_tree import renderers
from exactly_lib.util.description_tree.renderer import DetailsRenderer
from exactly_lib.util.symbol_table import SymbolTable


class Applier(ABC):
    @abstractmethod
    def apply(self) -> MatchingResult:
        pass


class Conf:
    def __init__(self,
                 name: str,
                 make_matcher: Callable[[str, FilesCondition, FilesMatcherModel], Applier],
                 ):
        self.name = name
        self.applier_for_model = make_matcher


class _Matcher(MatcherWTraceAndNegation[FilesMatcherModel]):
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

    @property
    def negation(self) -> FilesMatcher:
        return combinator_matchers.Negation(self)

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

    def value_of_any_dependency(self, tcds: Tcds) -> FilesMatcherAdv:
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


def _structure_name(matcher: str) -> str:
    return ' '.join((matcher, syntax_elements.FILES_CONDITION_SYNTAX_ELEMENT.singular_name))


EQUALS_STRUCTURE_NAME = _structure_name(config.EQUALS_ARGUMENT)
CONTAINS_STRUCTURE_NAME = _structure_name(config.CONTAINS_ARGUMENT)
