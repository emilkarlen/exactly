from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Callable, Iterator, ContextManager, Sequence

from exactly_lib.definitions import logic
from exactly_lib.symbol.logic.matcher import MatcherSdv
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.test_case_file_structure.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.description_tree import custom_details
from exactly_lib.test_case_utils.description_tree.tree_structured import WithCachedTreeStructureDescriptionBase
from exactly_lib.type_system.description.trace_building import TraceBuilder
from exactly_lib.type_system.description.tree_structured import StructureRenderer, WithTreeStructureDescription
from exactly_lib.type_system.logic.matcher_base_class import MatcherWTrace, MatchingResult, MatcherDdv, MatcherAdv, \
    ApplicationEnvironment
from exactly_lib.util import strings
from exactly_lib.util.description_tree import details, renderers
from exactly_lib.util.description_tree.renderer import DetailsRenderer
from exactly_lib.util.logic_types import Quantifier
from exactly_lib.util.strings import ToStringObject
from exactly_lib.util.symbol_table import SymbolTable

MODEL = TypeVar('MODEL')
ELEMENT = TypeVar('ELEMENT')


class ElementRendering(Generic[MODEL, ELEMENT]):
    def __init__(self,
                 type_name: str,
                 element_matcher_syntax_name: str,
                 renderer: Callable[[ELEMENT], DetailsRenderer],
                 ):
        self.type_name = type_name
        self.element_matcher_syntax_name = element_matcher_syntax_name
        self.renderer = renderer


class ElementSetup(Generic[MODEL, ELEMENT]):
    def __init__(self,
                 rendering: ElementRendering[MODEL, ELEMENT],
                 elements_getter: Callable[[Tcds, ApplicationEnvironment, MODEL], ContextManager[Iterator[ELEMENT]]],
                 ):
        self.rendering = rendering
        self.elements_getter = elements_getter


def sdv(setup: ElementSetup[MODEL, ELEMENT],
        quantifier: Quantifier,
        predicate: MatcherSdv[ELEMENT],
        ) -> MatcherSdv[MODEL]:
    return _QuantifierSdv(
        setup,
        quantifier,
        predicate,
    )


class _ApplicationConf(Generic[MODEL, ELEMENT]):
    def __init__(self,
                 setup: ElementSetup[MODEL, ELEMENT],
                 predicate: MatcherWTrace[ELEMENT],
                 tcds: Tcds,
                 environment: ApplicationEnvironment,
                 ):
        self.setup = setup
        self.predicate = predicate
        self.tcds = tcds
        self.environment = environment


class _QuantifierBase(Generic[MODEL, ELEMENT],
                      WithCachedTreeStructureDescriptionBase,
                      MatcherWTrace[MODEL],
                      ABC):
    def __init__(self,
                 quantifier: Quantifier,
                 conf: _ApplicationConf[MODEL, ELEMENT],
                 ):
        WithCachedTreeStructureDescriptionBase.__init__(self)
        self._conf = conf
        self._quantifier = quantifier

        self._name = self.__name(quantifier, conf.setup.rendering)

    @staticmethod
    def __name(quantifier: Quantifier,
               element_rendering: ElementRendering) -> str:
        return ' '.join((logic.QUANTIFIER_ARGUMENTS[quantifier],
                         element_rendering.type_name,
                         logic.QUANTIFICATION_SEPARATOR_ARGUMENT,
                         element_rendering.element_matcher_syntax_name,
                         ))

    @staticmethod
    def new_structure_tree(quantifier: Quantifier,
                           element_rendering: ElementRendering,
                           predicate: WithTreeStructureDescription) -> StructureRenderer:
        return renderers.NodeRendererFromParts(
            _QuantifierBase.__name(quantifier, element_rendering),
            None,
            (),
            (predicate.structure(),),
        )

    @property
    def name(self) -> str:
        return self._name

    def _structure(self) -> StructureRenderer:
        return self.new_structure_tree(self._quantifier,
                                       self._conf.setup.rendering,
                                       self._conf.predicate)

    def matches_w_trace(self, model: MODEL) -> MatchingResult:
        conf = self._conf
        predicate = conf.predicate
        with conf.setup.elements_getter(conf.tcds, conf.environment, model) as elements:
            return self._matches(
                TraceBuilder(self.name),
                predicate,
                elements,
            )

    def _matching_element_header(self) -> ToStringObject:
        return strings.FormatPositional('At least 1 {} matches', self._conf.setup.rendering.type_name)

    def _non_matching_element_header(self) -> ToStringObject:
        return strings.FormatPositional('At least 1 {} does not match', self._conf.setup.rendering.type_name)

    def _report_final_element(self,
                              tb: TraceBuilder,
                              result: MatchingResult,
                              element: ELEMENT) -> MatchingResult:
        header = (
            self._matching_element_header()
            if result.value
            else
            self._non_matching_element_header()
        )
        actual = custom_details.actual(
            details.HeaderAndValue(
                header,
                self._conf.setup.rendering.renderer(element),
            )
        )
        tb.append_details(actual)

        tb.append_child(result.trace)

        return tb.build_result(result.value)

    @abstractmethod
    def _matches(self,
                 tb: TraceBuilder,
                 predicate: MatcherWTrace[ELEMENT],
                 elements: Iterator[ELEMENT]) -> MatchingResult:
        pass

    def _explanation_when_no_element_matcher_trace(self, explanation: ToStringObject) -> DetailsRenderer:
        return custom_details.ExpectedAndActual(
            custom_details.TreeStructure(self._conf.predicate.structure()),
            details.String(explanation),
        )


class Exists(Generic[MODEL, ELEMENT], _QuantifierBase[MODEL, ELEMENT]):
    def __init__(self, conf: _ApplicationConf[MODEL, ELEMENT]):
        _QuantifierBase.__init__(self,
                                 Quantifier.EXISTS,
                                 conf,
                                 )

    def _no_match(self, tb: TraceBuilder, tot_num_elements: int) -> MatchingResult:
        explanation = strings.FormatPositional(
            'No {} matches ({} tested)', self._conf.setup.rendering.type_name,
            tot_num_elements,
        )
        return (
            tb
                .append_details(self._explanation_when_no_element_matcher_trace(explanation))
                .build_result(False)
        )

    def _matches(self,
                 tb: TraceBuilder,
                 predicate: MatcherWTrace[ELEMENT],
                 elements: Iterator[ELEMENT]) -> MatchingResult:
        num_elements = 0
        for element in elements:
            num_elements += 1
            result = predicate.matches_w_trace(element)
            if result.value:
                return self._report_final_element(tb, result, element)

        return self._no_match(tb, num_elements)


class ForAll(Generic[MODEL, ELEMENT], _QuantifierBase[MODEL, ELEMENT]):
    def __init__(self, conf: _ApplicationConf[MODEL, ELEMENT]):
        _QuantifierBase.__init__(self,
                                 Quantifier.ALL,
                                 conf,
                                 )

    def _all_match(self, tb: TraceBuilder, tot_num_elements: int) -> MatchingResult:
        actual = details.String(
            strings.FormatPositional('Every {} matches ({} tested)', self._conf.setup.rendering.type_name,
                                     tot_num_elements,
                                     )
        )
        expected = custom_details.TreeStructure(self._conf.predicate.structure())
        return (
            tb
                .append_details(custom_details.expected(expected))
                .append_details(custom_details.actual(actual))
                .build_result(True)
        )

    def _matches(self,
                 tb: TraceBuilder,
                 predicate: MatcherWTrace[ELEMENT],
                 elements: Iterator[ELEMENT]) -> MatchingResult:
        num_elements = 0
        for element in elements:
            num_elements += 1
            result = predicate.matches_w_trace(element)
            if not result.value:
                return self._report_final_element(tb, result, element)

        return self._all_match(tb, num_elements)


class _QuantifierAdv(Generic[MODEL, ELEMENT], MatcherAdv[MODEL]):
    MATCHER_MAKER = {
        Quantifier.ALL: ForAll,
        Quantifier.EXISTS: Exists,
    }

    def __init__(self,
                 quantifier: Quantifier,
                 setup: ElementSetup[MODEL, ELEMENT],
                 predicate: MatcherAdv[ELEMENT],
                 tcds: Tcds,
                 ):
        self._quantifier = quantifier
        self._element_setup = setup
        self._predicate = predicate
        self._tcds = tcds

    def primitive(self, environment: ApplicationEnvironment) -> MatcherWTrace[MODEL]:
        conf = _ApplicationConf(self._element_setup,
                                self._predicate.primitive(environment),
                                self._tcds,
                                environment)
        return self.MATCHER_MAKER[self._quantifier](conf)


class _QuantifierDdv(Generic[MODEL, ELEMENT], MatcherDdv[MODEL]):
    def __init__(self,
                 quantifier: Quantifier,
                 setup: ElementSetup[MODEL, ELEMENT],
                 predicate: MatcherDdv[ELEMENT],
                 ):
        self._quantifier = quantifier
        self._element_setup = setup
        self._predicate = predicate

    def structure(self) -> StructureRenderer:
        return _QuantifierBase.new_structure_tree(self._quantifier,
                                                  self._element_setup.rendering,
                                                  self._predicate)

    @property
    def validator(self) -> DdvValidator:
        return self._predicate.validator

    def value_of_any_dependency(self, tcds: Tcds) -> MatcherAdv[MODEL]:
        return _QuantifierAdv(self._quantifier,
                              self._element_setup,
                              self._predicate.value_of_any_dependency(tcds),
                              tcds,
                              )


class _QuantifierSdv(Generic[MODEL, ELEMENT], MatcherSdv[MODEL]):
    def __init__(self,
                 setup: ElementSetup[MODEL, ELEMENT],
                 quantifier: Quantifier,
                 predicate: MatcherSdv[ELEMENT],
                 ):
        self._setup = setup
        self._quantifier = quantifier
        self._predicate = predicate

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._predicate.references

    def resolve(self, symbols: SymbolTable) -> MatcherDdv[MODEL]:
        return _QuantifierDdv(
            self._quantifier,
            self._setup,
            self._predicate.resolve(symbols),
        )
