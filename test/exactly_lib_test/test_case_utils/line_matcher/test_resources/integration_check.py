import unittest
from typing import Optional, Sequence

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.logic.line_matcher import LineMatcherResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_utils.line_matcher import parse_line_matcher as sut
from exactly_lib.type_system.error_message import ErrorMessageResolver
from exactly_lib.type_system.logic.hard_error import HardErrorException
from exactly_lib.type_system.logic.line_matcher import LineMatcherValue, LineMatcher, LineMatcherLine
from exactly_lib.util.symbol_table import SymbolTable, symbol_table_from_none_or_value
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_home_and_sds
from exactly_lib_test.test_case_utils.test_resources.validation import ValidationExpectation, all_validations_passes
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


class Arrangement:
    def __init__(self, symbols: Optional[SymbolTable] = None):
        self.symbols = symbol_table_from_none_or_value(symbols)


class Expectation:
    def __init__(
            self,
            source: ValueAssertion[ParseSource] = asrt.anything_goes(),
            symbol_references: ValueAssertion[Sequence[SymbolReference]] = asrt.is_empty_sequence,
            validation: ValidationExpectation = all_validations_passes(),
            main_result: Optional[ValueAssertion[Optional[str]]] = None,
            is_hard_error: Optional[ValueAssertion[str]] = None,
    ):
        self.source = source
        self.symbol_references = symbol_references
        self.validation = validation
        self.main_result = main_result
        self.is_hard_error = is_hard_error


is_pass = Expectation


def main_result_is_success() -> Optional[ValueAssertion[Optional[str]]]:
    return None


def main_result_is_failure(error_message: ValueAssertion[Optional[str]] = asrt.is_instance(str)
                           ) -> Optional[ValueAssertion[Optional[str]]]:
    return error_message


def check(put: unittest.TestCase,
          source: ParseSource,
          model: LineMatcherLine,
          arrangement: Arrangement,
          expectation: Expectation):
    _Checker(put, source, model, sut.parser(), arrangement, expectation).check()


def check_with_custom_parser(put: unittest.TestCase,
                             source: ParseSource,
                             model: LineMatcherLine,
                             parser: Parser[LineMatcherResolver],
                             arrangement: Arrangement,
                             expectation: Expectation):
    _Checker(put, source, model, parser, arrangement, expectation).check()


class _CheckIsDoneException(Exception):
    pass


class _Checker:
    def __init__(self,
                 put: unittest.TestCase,
                 source: ParseSource,
                 model: LineMatcherLine,
                 parser: Parser[LineMatcherResolver],
                 arrangement: Arrangement,
                 expectation: Expectation):
        self.put = put
        self.source = source
        self.model = model
        self.parser = parser
        self.arrangement = arrangement
        self.expectation = expectation
        self.tcds = fake_home_and_sds()

    def check(self):
        try:
            self._check()
        except _CheckIsDoneException:
            pass

    def _check(self):
        matcher_resolver = self._parse()

        self.expectation.symbol_references.apply_with_message(self.put,
                                                              matcher_resolver.references,
                                                              'reference')

        matcher_value = self._resolve_value(matcher_resolver)

        self._check_validation_pre_sds(matcher_value)
        self._check_validation_post_sds(matcher_value)

        matcher = self._resolve_primitive_value(matcher_value)

        self._check_application(matcher)

    def _parse(self) -> LineMatcherResolver:
        resolver = self.parser.parse(self.source)
        asrt.is_instance(LineMatcherResolver).apply_with_message(self.put,
                                                                 resolver,
                                                                 'resolver')
        assert isinstance(resolver, LineMatcherResolver)

        self.expectation.source.apply_with_message(self.put,
                                                   self.source,
                                                   'source after parse')

        return resolver

    def _resolve_value(self, matcher_resolver: LineMatcherResolver) -> LineMatcherValue:
        matcher_value = matcher_resolver.resolve(self.arrangement.symbols)

        asrt.is_instance(LineMatcherValue).apply_with_message(self.put,
                                                              matcher_value,
                                                              'resolved value')

        assert isinstance(matcher_value, LineMatcherValue)

        return matcher_value

    def _resolve_primitive_value(self, matcher_value: LineMatcherValue) -> LineMatcher:
        ret_val = matcher_value.value_of_any_dependency(self.tcds)

        asrt.is_instance(LineMatcher).apply_with_message(self.put,
                                                         ret_val,
                                                         'primitive value')

        assert isinstance(ret_val, LineMatcher)

        return ret_val

    def _check_validation_pre_sds(self, matcher_value: LineMatcherValue):
        result = matcher_value.validator().validate_pre_sds_if_applicable(self.tcds.hds)

        self.expectation.validation.pre_sds.apply_with_message(self.put,
                                                               result,
                                                               'validation pre sds')

        if result is not None:
            raise _CheckIsDoneException()

    def _check_validation_post_sds(self, matcher_value: LineMatcherValue):
        result = matcher_value.validator().validate_post_sds_if_applicable(self.tcds)

        self.expectation.validation.post_sds.apply_with_message(self.put,
                                                                result,
                                                                'validation post sds')

        if result is not None:
            raise _CheckIsDoneException()

    def _check_application(self, matcher: LineMatcher):
        try:
            main_result = matcher.matches2(self.model)
            self._check_application_result(main_result)
        except HardErrorException as ex:
            self._check_hard_error(ex)

    def _check_application_result(self, result: Optional[ErrorMessageResolver]):
        if self.expectation.is_hard_error is not None:
            self.put.fail('HARD_ERROR not reported (raised)')

        if self.expectation.main_result is None:
            self.put.assertIsNone(result,
                                  'result from main')
        else:
            self.put.assertIsNotNone(result,
                                     'result from main')
            err_msg = result.resolve()
            self.expectation.main_result.apply_with_message(self.put, err_msg,
                                                            'error result of main')

    def _check_hard_error(self, result: HardErrorException):
        if self.expectation.is_hard_error is None:
            self.put.fail('Unexpected HARD_ERROR')
        else:
            assertion_on_text_renderer = asrt_text_doc.is_string_for_test(self.expectation.is_hard_error)
            assertion_on_text_renderer.apply_with_message(self.put, result.error,
                                                          'error message for hard error')
            raise _CheckIsDoneException()
