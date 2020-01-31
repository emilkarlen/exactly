import unittest
from abc import ABC, abstractmethod
from typing import Callable, TypeVar, Generic, Optional

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.symbol.logic.matcher import MatcherSdv
from exactly_lib.test_case.validation.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.matcher.impls.sdv_components import MatcherSdvFromParts
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.files_matcher import FilesMatcherModel
from exactly_lib.type_system.logic.impls.advs import MatcherAdvFromFunction
from exactly_lib.type_system.logic.logic_base_class import ApplicationEnvironment
from exactly_lib.type_system.logic.matcher_base_class import MatcherWTraceAndNegation, MatchingResult, MatcherDdv, \
    MatcherAdv
from exactly_lib.util.description_tree import renderers, tree
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.test_case_utils.matcher.test_resources.matchers import MatcherDdvFromParts2TestImpl
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion, MessageBuilder

ACTUAL = TypeVar('ACTUAL')
ACTUAL_PRE_SDS = TypeVar('ACTUAL_PRE_SDS')
ACTUAL_POST_SDS = TypeVar('ACTUAL_POST_SDS')
MODEL = TypeVar('MODEL')


class ApplicationAssertionSetup(Generic[MODEL, ACTUAL], ABC):
    @abstractmethod
    def get_assertion(self, symbols: SymbolTable, tcds: Tcds, env: ApplicationEnvironment) -> ValueAssertion[ACTUAL]:
        pass

    @abstractmethod
    def get_actual(self, model: MODEL) -> ACTUAL:
        pass


class ValidationAssertionSetup(Generic[ACTUAL_PRE_SDS, ACTUAL_POST_SDS], ABC):
    @abstractmethod
    def get_pre_sds_assertion(self, hds: HomeDirectoryStructure) -> ValueAssertion[ACTUAL_PRE_SDS]:
        pass

    @abstractmethod
    def get_pre_sds_actual(self, hds: HomeDirectoryStructure) -> ACTUAL_PRE_SDS:
        pass

    @abstractmethod
    def get_post_sds_assertion(self, tcds: Tcds) -> ValueAssertion[ACTUAL_POST_SDS]:
        pass

    @abstractmethod
    def get_post_sds_actual(self, tcds: Tcds) -> ACTUAL_POST_SDS:
        pass


class UnconditionallyPassValidationAssertionSetup(ValidationAssertionSetup):
    def get_pre_sds_assertion(self, hds: HomeDirectoryStructure) -> ValueAssertion:
        return asrt.anything_goes()

    def get_pre_sds_actual(self, hds: HomeDirectoryStructure):
        return None

    def get_post_sds_assertion(self, tcds: Tcds) -> ValueAssertion:
        return asrt.anything_goes()

    def get_post_sds_actual(self, tcds: Tcds):
        return None


class UnconditionallyPassApplicationAssertionSetup(ApplicationAssertionSetup):
    def get_assertion(self, symbols: SymbolTable, tcds: Tcds, env: ApplicationEnvironment) -> ValueAssertion:
        return asrt.anything_goes()

    def get_actual(self, model: MODEL):
        return None


def matcher(put: unittest.TestCase,
            validation_assertion: ValidationAssertionSetup[ACTUAL_PRE_SDS, ACTUAL_POST_SDS]
            = UnconditionallyPassValidationAssertionSetup(),

            application_assertion: ApplicationAssertionSetup[MODEL, ACTUAL]
            = UnconditionallyPassApplicationAssertionSetup(),

            message_builder: MessageBuilder = MessageBuilder.new_empty(),
            matching_result: bool = True,
            ) -> MatcherSdv[MODEL]:
    def make_ddv(symbols: SymbolTable) -> MatcherDdv[MODEL]:
        def make_adv(tcds: Tcds) -> MatcherAdv[MODEL]:
            def make_matcher(environment: ApplicationEnvironment) -> MatcherWTraceAndNegation[MODEL]:
                return MatcherThatAppliesValueAssertion(
                    put,
                    application_assertion.get_assertion(symbols, tcds, environment),
                    application_assertion.get_actual,
                    message_builder,
                    matching_result,
                )

            return MatcherAdvFromFunction(make_matcher)

        return MatcherDdvFromParts2TestImpl(
            make_adv,
            MatcherThatAppliesValueAssertion.STRUCTURE,
            ValidatorThatAppliesValueAssertions(put, validation_assertion, message_builder)
        )

    return MatcherSdvFromParts(
        (),
        make_ddv,
    )


class ValidatorThatAppliesValueAssertions(Generic[ACTUAL_PRE_SDS, ACTUAL_POST_SDS], DdvValidator):
    def __init__(self,
                 put: unittest.TestCase,
                 setup: ValidationAssertionSetup[ACTUAL_PRE_SDS, ACTUAL_POST_SDS],
                 message_builder: MessageBuilder,
                 ):
        self._put = put
        self._setup = setup
        self._message_builder = message_builder

    def validate_pre_sds_if_applicable(self, hds: HomeDirectoryStructure) -> Optional[TextRenderer]:
        self._setup.get_pre_sds_assertion(hds).apply(
            self._put,
            self._setup.get_pre_sds_actual(hds),
            self._message_builder.for_sub_component('validation/pre sds')
        )

        return None

    def validate_post_sds_if_applicable(self, tcds: Tcds) -> Optional[TextRenderer]:
        self._setup.get_post_sds_assertion(tcds).apply(
            self._put,
            self._setup.get_post_sds_actual(tcds),
            self._message_builder.for_sub_component('validation/post sds')
        )

        return None


class MatcherThatAppliesValueAssertion(Generic[MODEL, ACTUAL], MatcherWTraceAndNegation[MODEL]):
    NAME = 'MatcherThatAppliesValueAssertion'
    STRUCTURE = renderers.header_only(NAME)

    def __init__(self,
                 put: unittest.TestCase,
                 assertion: ValueAssertion[ACTUAL],
                 get_actual: Callable[[MODEL], ACTUAL],
                 message_builder: MessageBuilder,
                 matching_result: bool,
                 ):
        self.put = put
        self.assertion = assertion
        self.get_actual = get_actual
        self.message_builder = message_builder
        self.matching_result = matching_result

    @property
    def name(self) -> str:
        return str(type(self))

    def structure(self) -> StructureRenderer:
        return self.STRUCTURE

    @property
    def negation(self) -> MatcherWTraceAndNegation[FilesMatcherModel]:
        return MatcherThatAppliesValueAssertion(self.put,
                                                self.assertion,
                                                self.get_actual,
                                                self.message_builder,
                                                not self.matching_result)

    def matches_w_trace(self, model: FilesMatcherModel) -> MatchingResult:
        self._apply_assertion(model)
        return self._matching_result()

    def _apply_assertion(self, model: FilesMatcherModel):
        actual = self.get_actual(model)
        self.assertion.apply(
            self.put,
            actual,
            self.message_builder.for_sub_component('application'),
        )

    def _matching_result(self) -> MatchingResult:
        return MatchingResult(self.matching_result,
                              renderers.Constant(
                                  tree.Node.empty(self.name, self.matching_result)
                              ))
