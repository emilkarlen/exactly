import unittest
from typing import Optional, Sequence, Callable

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.logic.string_transformer import StringTransformerResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_utils.string_transformer import parse_string_transformer
from exactly_lib.type_system.logic.hard_error import HardErrorException
from exactly_lib.type_system.logic.string_transformer import StringTransformer, StringTransformerValue, \
    StringTransformerModel
from exactly_lib.util.symbol_table import SymbolTable, symbol_table_from_none_or_value
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_home_and_sds
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.test_case_utils.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check__for_expression_parser
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
            main_result: ValueAssertion[StringTransformerModel] = asrt.anything_goes(),
            is_hard_error: Optional[ValueAssertion[str]] = None,
    ):
        self.source = source
        self.symbol_references = symbol_references
        self.validation = validation
        self.main_result = main_result
        self.is_hard_error = is_hard_error


is_pass = Expectation


def check(put: unittest.TestCase,
          source: ParseSource,
          model: StringTransformerModel,
          arrangement: Arrangement,
          expectation: Expectation):
    _Checker(put, source, model, parse_string_transformer.parser(), arrangement, expectation).check()


def check_with_custom_parser(put: unittest.TestCase,
                             source: ParseSource,
                             model: StringTransformerModel,
                             parser: Parser[StringTransformerResolver],
                             arrangement: Arrangement,
                             expectation: Expectation):
    _Checker(put, source, model, parser, arrangement, expectation).check()


class TestCaseWithCheckMethods(unittest.TestCase):
    def _check(self,
               source: ParseSource,
               model: StringTransformerModel,
               arrangement: Arrangement,
               expectation: Expectation
               ):
        check(self, source, model, arrangement, expectation)

    def _check_with_source_variants(self,
                                    arguments: Arguments,
                                    get_model: Callable[[], StringTransformerModel],
                                    arrangement: Arrangement,
                                    expectation: Expectation
                                    ):
        for source in equivalent_source_variants__with_source_check__for_expression_parser(self, arguments):
            self._check(source, get_model(), arrangement, expectation)


class _CheckIsDoneException(Exception):
    pass


class _Checker:
    def __init__(self,
                 put: unittest.TestCase,
                 source: ParseSource,
                 model: StringTransformerModel,
                 parser: Parser[StringTransformerResolver],
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
        transformer_resolver = self._parse()

        self.expectation.symbol_references.apply_with_message(self.put,
                                                              transformer_resolver.references,
                                                              'reference')

        transformer_value = self._resolve_value(transformer_resolver)

        self._check_validation_pre_sds(transformer_value)
        self._check_validation_post_sds(transformer_value)

        transformer = self._resolve_primitive_value(transformer_value)

        self._check_application(transformer)

    def _parse(self) -> StringTransformerResolver:
        resolver = self.parser.parse(self.source)
        asrt.is_instance(StringTransformerResolver).apply_with_message(self.put,
                                                                       resolver,
                                                                       'resolver')
        assert isinstance(resolver, StringTransformerResolver)

        self.expectation.source.apply_with_message(self.put,
                                                   self.source,
                                                   'source after parse')

        return resolver

    def _resolve_value(self, transformer_resolver: StringTransformerResolver) -> StringTransformerValue:
        transformer_value = transformer_resolver.resolve(self.arrangement.symbols)

        asrt.is_instance(StringTransformerValue).apply_with_message(self.put,
                                                                    transformer_value,
                                                                    'resolved value')

        assert isinstance(transformer_value, StringTransformerValue)

        return transformer_value

    def _resolve_primitive_value(self, transformer_value: StringTransformerValue) -> StringTransformer:
        ret_val = transformer_value.value_of_any_dependency(self.tcds)

        asrt.is_instance(StringTransformer).apply_with_message(self.put,
                                                               ret_val,
                                                               'primitive value')

        assert isinstance(ret_val, StringTransformer)

        return ret_val

    def _check_validation_pre_sds(self, transformer_value: StringTransformerValue):
        result = transformer_value.validator().validate_pre_sds_if_applicable(self.tcds.hds)

        self.expectation.validation.pre_sds.apply_with_message(self.put,
                                                               result,
                                                               'validation/pre sds')

        if result is not None:
            raise _CheckIsDoneException()

    def _check_validation_post_sds(self, transformer_value: StringTransformerValue):
        result = transformer_value.validator().validate_post_sds_if_applicable(self.tcds)

        self.expectation.validation.post_sds.apply_with_message(self.put,
                                                                result,
                                                                'validation/post sds')

        if result is not None:
            raise _CheckIsDoneException()

    def _check_application(self, transformer: StringTransformer):
        try:
            main_result = transformer.transform(self.model)
            self._check_application_result(main_result)
        except HardErrorException as ex:
            self._check_hard_error(ex)

    def _check_application_result(self, result: StringTransformerModel):
        if self.expectation.is_hard_error is not None:
            self.put.fail('HARD_ERROR not reported (raised)')

        self.expectation.main_result.apply_with_message(self.put,
                                                        result,
                                                        'result of main')

    def _check_hard_error(self, result: HardErrorException):
        if self.expectation.is_hard_error is None:
            self.put.fail('Unexpected HARD_ERROR')
        else:
            assertion_on_text_renderer = asrt_text_doc.is_string_for_test(self.expectation.is_hard_error)
            assertion_on_text_renderer.apply_with_message(self.put, result.error,
                                                          'error message for hard error')
            raise _CheckIsDoneException()
