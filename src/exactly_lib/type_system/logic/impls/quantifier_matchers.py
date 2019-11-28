from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Callable, Iterator, Optional, ContextManager

from exactly_lib.definitions import instruction_arguments
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.description_tree.tree_structured import WithCachedTreeStructureDescriptionBase
from exactly_lib.test_case_utils.err_msg import err_msg_resolvers
from exactly_lib.type_system.description.trace_building import TraceBuilder
from exactly_lib.type_system.description.tree_structured import StructureRenderer, WithTreeStructureDescription
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.logic.impls import combinator_matchers
from exactly_lib.type_system.logic.matcher_base_class import MatcherWTrace, MatchingResult, MatcherWTraceAndNegation, \
    MatcherDdv
from exactly_lib.util import strings
from exactly_lib.util.description_tree import details, renderers
from exactly_lib.util.description_tree.renderer import DetailsRenderer
from exactly_lib.util.logic_types import Quantifier
from exactly_lib.util.strings import ToStringObject

MODEL = TypeVar('MODEL')
ELEMENT = TypeVar('ELEMENT')


class ElementSetup(Generic[MODEL, ELEMENT]):
    def __init__(self,
                 type_name: str,
                 element_matcher_syntax_name: str,
                 elements_getter: Callable[[MODEL], ContextManager[Iterator[ELEMENT]]],
                 renderer: Callable[[ELEMENT], DetailsRenderer],
                 ):
        self.type_name = type_name
        self.element_matcher_syntax_name = element_matcher_syntax_name
        self.elements_getter = elements_getter
        self.renderer = renderer


class _QuantifierBase(Generic[MODEL, ELEMENT],
                      WithCachedTreeStructureDescriptionBase,
                      MatcherWTraceAndNegation[MODEL],
                      ABC):
    def __init__(self,
                 quantifier: Quantifier,
                 element_setup: ElementSetup,
                 predicate: MatcherWTrace[ELEMENT],
                 ):
        WithCachedTreeStructureDescriptionBase.__init__(self)
        self._quantifier = quantifier
        self._element_setup = element_setup
        self._predicate = predicate

        self._name = self._name(quantifier, element_setup)

    @staticmethod
    def _name(quantifier: Quantifier,
              element_setup: ElementSetup) -> str:
        return ' '.join((instruction_arguments.QUANTIFIER_ARGUMENTS[quantifier],
                         element_setup.type_name,
                         instruction_arguments.QUANTIFICATION_SEPARATOR_ARGUMENT,
                         element_setup.element_matcher_syntax_name,
                         ))

    @staticmethod
    def new_structure_tree(quantifier: Quantifier,
                           element_setup: ElementSetup,
                           predicate: WithTreeStructureDescription) -> StructureRenderer:
        return renderers.NodeRendererFromParts(
            _QuantifierBase._name(quantifier, element_setup),
            None,
            (),
            (predicate.structure(),),
        )

    @property
    def name(self) -> str:
        return self._name

    def _structure(self) -> StructureRenderer:
        return self.new_structure_tree(self._quantifier,
                                       self._element_setup,
                                       self._predicate)

    @property
    def option_description(self) -> str:
        return self.name

    def negation(self) -> MatcherWTraceAndNegation[MODEL]:
        return combinator_matchers.Negation(self)

    def matches(self, model: MODEL) -> bool:
        return self.matches_w_trace(model).value

    def matches_emr(self, model: MODEL) -> Optional[ErrorMessageResolver]:
        result = self.matches_w_trace(model)
        return (
            None
            if result.value
            else
            err_msg_resolvers.constant(' '.join([self.name, str(result.value)]))
        )

    def matches_w_trace(self, model: MODEL) -> MatchingResult:
        with self._element_setup.elements_getter(model) as elements:
            return self._matches(
                TraceBuilder(self.name),
                self._element_setup.renderer,
                self._predicate,
                elements,
            )

    def _matching_element_header(self) -> ToStringObject:
        return strings.Concatenate(('Matching ', self._element_setup.type_name))

    def _non_matching_element_header(self) -> ToStringObject:
        return strings.Concatenate(('Non-matching ', self._element_setup.type_name))

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
        tb.append_details(details.HeaderAndValue(
            header,
            self._element_setup.renderer(element),
        ))

        tb.append_child(result.trace)

        return tb.build_result(result.value)

    @abstractmethod
    def _matches(self,
                 tb: TraceBuilder,
                 renderer: Callable[[ELEMENT], DetailsRenderer],
                 predicate: MatcherWTrace[ELEMENT],
                 elements: Iterator[ELEMENT]) -> MatchingResult:
        pass


class Exists(Generic[MODEL, ELEMENT], _QuantifierBase[MODEL, ELEMENT]):
    def __init__(self,
                 element_setup: ElementSetup,
                 predicate: MatcherWTrace[ELEMENT],
                 ):
        _QuantifierBase.__init__(self,
                                 Quantifier.EXISTS,
                                 element_setup,
                                 predicate,
                                 )

    def _no_match(self, tb: TraceBuilder, tot_num_elements: int) -> MatchingResult:
        return (
            tb.append_details(
                details.String(
                    strings.FormatPositional(
                        'No matching {} ({} tested)',
                        self._element_setup.type_name,
                        tot_num_elements,
                    )
                )
            ).build_result(False)
        )

    def _matches(self,
                 tb: TraceBuilder,
                 renderer: Callable[[ELEMENT], DetailsRenderer],
                 predicate: MatcherWTrace[ELEMENT],
                 elements: Iterator[ELEMENT]) -> MatchingResult:
        num_elements = 0
        for element in elements:
            num_elements += 1
            result = predicate.matches_w_trace(element)
            if result.value:
                return self._report_final_element(tb, result, element)

        return self._no_match(tb, num_elements)


class ExistsDdv(Generic[MODEL, ELEMENT], MatcherDdv[MODEL]):
    def __init__(self,
                 element_setup: ElementSetup,
                 predicate: MatcherDdv[ELEMENT],
                 ):
        self._element_setup = element_setup
        self._predicate = predicate

    def value_of_any_dependency(self, tcds: Tcds) -> MatcherWTraceAndNegation[MODEL]:
        return Exists(
            self._element_setup,
            self._predicate.value_of_any_dependency(tcds)
        )

    def structure(self) -> StructureRenderer:
        return _QuantifierBase.new_structure_tree(Quantifier.EXISTS,
                                                  self._element_setup,
                                                  self._predicate)


class ForAll(Generic[MODEL, ELEMENT], _QuantifierBase[MODEL, ELEMENT]):
    def __init__(self,
                 element_setup: ElementSetup,
                 predicate: MatcherWTrace[ELEMENT],
                 ):
        _QuantifierBase.__init__(self,
                                 Quantifier.ALL,
                                 element_setup,
                                 predicate,
                                 )

    def _all_match(self, tb: TraceBuilder, tot_num_elements: int) -> MatchingResult:
        return (
            tb.append_details(
                details.String(
                    strings.FormatPositional(
                        'Every {} matches ({} tested)',
                        self._element_setup.type_name,
                        tot_num_elements,
                    )
                )
            ).build_result(True)
        )

    def _matches(self,
                 tb: TraceBuilder,
                 renderer: Callable[[ELEMENT], DetailsRenderer],
                 predicate: MatcherWTrace[ELEMENT],
                 elements: Iterator[ELEMENT]) -> MatchingResult:
        num_elements = 0
        for element in elements:
            num_elements += 1
            result = predicate.matches_w_trace(element)
            if not result.value:
                return self._report_final_element(tb, result, element)

        return self._all_match(tb, num_elements)


class ForAllDdv(Generic[MODEL, ELEMENT], MatcherDdv[MODEL]):
    def __init__(self,
                 element_setup: ElementSetup,
                 predicate: MatcherDdv[ELEMENT],
                 ):
        self._element_setup = element_setup
        self._predicate = predicate

    def value_of_any_dependency(self, tcds: Tcds) -> MatcherWTraceAndNegation[MODEL]:
        return ForAll(
            self._element_setup,
            self._predicate.value_of_any_dependency(tcds)
        )

    def structure(self) -> StructureRenderer:
        return _QuantifierBase.new_structure_tree(Quantifier.ALL,
                                                  self._element_setup,
                                                  self._predicate)
