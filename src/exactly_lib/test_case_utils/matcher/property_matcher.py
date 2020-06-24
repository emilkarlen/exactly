from typing import Generic, TypeVar, Sequence

from exactly_lib.symbol.logic.matcher import MODEL, MatcherSdv
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.test_case_file_structure import ddv_validators
from exactly_lib.test_case_file_structure.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.matcher.property_getter import PropertyGetter, PropertyGetterDdv, \
    PropertyGetterSdv, PropertyGetterAdv
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult, MatcherWTrace, MatcherDdv, \
    TraceRenderer, MatcherAdv, ApplicationEnvironment
from exactly_lib.util.symbol_table import SymbolTable

PROP_TYPE = TypeVar('PROP_TYPE')


class PropertyMatcherDescriber:
    def trace(self,
              matcher_result: MatchingResult,
              property_getter: StructureRenderer,
              ) -> TraceRenderer:
        pass

    def structure(self,
                  matcher: StructureRenderer,
                  property_getter: StructureRenderer,
                  ) -> StructureRenderer:
        pass


class PropertyMatcher(Generic[MODEL, PROP_TYPE], MatcherWTrace[MODEL]):
    """Matches a property of a model"""

    def __init__(self,
                 matcher: MatcherWTrace[PROP_TYPE],
                 property_getter: PropertyGetter[MODEL, PROP_TYPE],
                 describer: PropertyMatcherDescriber,
                 ):
        self._matcher = matcher
        self._property_getter = property_getter
        self._describer = describer
        self._structure = self._describer.structure(matcher.structure(),
                                                    property_getter.structure())

    @property
    def name(self) -> str:
        """TODO Temp helper that should be removed after usages removed"""
        return 'PropertyMatcher deprecated'

    def structure(self) -> StructureRenderer:
        return self._structure

    def matches_w_trace(self, model: MODEL) -> MatchingResult:
        """
        :raises HardErrorException
        """
        matcher_result = self._matcher.matches_w_trace(self._property_getter.get_from(model))
        return MatchingResult(
            matcher_result.value,
            self._describer.trace(matcher_result,
                                  self._property_getter.structure())
        )


class _PropertyMatcherAdv(Generic[MODEL, PROP_TYPE], MatcherAdv[MODEL]):
    def __init__(self,
                 matcher: MatcherAdv[PROP_TYPE],
                 property_getter: PropertyGetterAdv[MODEL, PROP_TYPE],
                 describer: PropertyMatcherDescriber,
                 ):
        self._matcher = matcher
        self._property_getter = property_getter
        self._describer = describer

    def primitive(self, environment: ApplicationEnvironment) -> MatcherWTrace[MODEL]:
        return PropertyMatcher(
            self._matcher.primitive(environment),
            self._property_getter.applier(environment),
            self._describer,
        )


class PropertyMatcherDdv(Generic[MODEL, PROP_TYPE], MatcherDdv[MODEL]):
    def __init__(self,
                 matcher: MatcherDdv[PROP_TYPE],
                 property_getter: PropertyGetterDdv[MODEL, PROP_TYPE],
                 describer: PropertyMatcherDescriber,
                 ):
        self._matcher = matcher
        self._property_getter = property_getter
        self._describer = describer
        self._validator = ddv_validators.all_of([
            self._matcher.validator,
            self._property_getter.validator,
        ])

    def structure(self) -> StructureRenderer:
        return self._describer.structure(self._matcher.structure(),
                                         self._property_getter.structure())

    @property
    def validator(self) -> DdvValidator:
        return self._validator

    def value_of_any_dependency(self, tcds: Tcds) -> MatcherAdv[MODEL]:
        return _PropertyMatcherAdv(
            self._matcher.value_of_any_dependency(tcds),
            self._property_getter.value_of_any_dependency(tcds),
            self._describer,
        )


class PropertyMatcherSdv(Generic[MODEL, PROP_TYPE], MatcherSdv[MODEL]):
    def __init__(self,
                 matcher: MatcherSdv[PROP_TYPE],
                 property_getter: PropertyGetterSdv[MODEL, PROP_TYPE],
                 describer: PropertyMatcherDescriber,
                 ):
        self._matcher = matcher
        self._property_getter = property_getter
        self._describer = describer
        self._references = list(property_getter.references) + list(matcher.references)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def resolve(self, symbols: SymbolTable) -> PropertyMatcherDdv[MODEL, PROP_TYPE]:
        return PropertyMatcherDdv(
            self._matcher.resolve(symbols),
            self._property_getter.resolve(symbols),
            self._describer,
        )
