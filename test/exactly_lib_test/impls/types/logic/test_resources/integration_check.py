"""
Tools for integration testing of logic values the use the XDV-structure:

 - SDV
 - DDV
 - ADV
 - primitive
"""
import unittest
from types import MappingProxyType
from typing import Sequence, Generic, Any, Mapping

from exactly_lib.section_document.element_parsers.ps_or_tp.parser import Parser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.type_val_deps.dep_variants.sdv.full_deps.sdv import FullDepsSdv
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.impls.types.logic.test_resources.execution_check import ExecutionChecker
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import Arrangement, ParseExpectation, \
    PrimAndExeExpectation, Expectation, MultiSourceExpectation
from exactly_lib_test.impls.types.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.impls.types.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__for_expression_parser, \
    equivalent_source_variants__for_expression_parser_2, \
    equivalent_source_variants__with_source_check__for_full_line_expression_parser, \
    SourceStr2SourceVariants, \
    equivalent_source_variants__for_expr_parse__s__nsc
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.tcfs.test_resources.fake_ds import fake_tcds
from exactly_lib_test.test_resources.source import layout
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.source.layout import LayoutSpec
from exactly_lib_test.test_resources.test_utils import NExArr, NEA
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.dep_variants.test_resources.full_deps.common_properties_checker import \
    CommonPropertiesConfiguration, OUTPUT, INPUT, PRIMITIVE


class IntegrationChecker(Generic[PRIMITIVE, INPUT, OUTPUT]):
    """
    Tests object of a single type.

    A single instance may be used for multiple tests.
    """

    def __init__(self,
                 parser: Parser[FullDepsSdv[PRIMITIVE]],
                 configuration: CommonPropertiesConfiguration[PRIMITIVE, INPUT, OUTPUT],
                 check_application_result_with_tcds: bool,
                 ):
        """
        :param parser: Parser of objects of the tested type.
        :param configuration: Properties common to all objects of the tested type.
        """
        self._parser = parser
        self._configuration = configuration
        self._check_application_result_with_tcds = check_application_result_with_tcds

    @property
    def parser(self) -> Parser[FullDepsSdv[PRIMITIVE]]:
        return self._parser

    def check(self,
              put: unittest.TestCase,
              source: ParseSource,
              input_: INPUT,
              arrangement: Arrangement,
              expectation: Expectation[PRIMITIVE, OUTPUT],
              ):
        checker = _ParseAndExecutionChecker(put,
                                            input_,
                                            self._parser,
                                            arrangement,
                                            self._configuration,
                                            self._check_application_result_with_tcds,
                                            expectation)
        checker.check(source)

    def check__abs_stx(self,
                       put: unittest.TestCase,
                       source: AbstractSyntax,
                       input_: INPUT,
                       arrangement: Arrangement,
                       expectation: Expectation[PRIMITIVE, OUTPUT],
                       layout_: LayoutSpec = LayoutSpec.of_default(),
                       ):
        checker = _ParseAndExecutionChecker(put,
                                            input_,
                                            self._parser,
                                            arrangement,
                                            self._configuration,
                                            self._check_application_result_with_tcds,
                                            expectation)
        checker.check(remaining_source(source.tokenization().layout(layout_)))

    def check__abs_stx__wo_input(self,
                                 put: unittest.TestCase,
                                 source: AbstractSyntax,
                                 arrangement: Arrangement,
                                 expectation: Expectation[PRIMITIVE, OUTPUT],
                                 layout_: LayoutSpec = LayoutSpec.of_default(),
                                 ):
        self.check__abs_stx(
            put,
            source,
            None,
            arrangement,
            expectation,
            layout_,
        )

    def check__abs_stx__layouts__source_variants(
            self,
            put: unittest.TestCase,
            mk_source_variants: SourceStr2SourceVariants,
            source: AbstractSyntax,
            input_: INPUT,
            arrangement: Arrangement,
            expectation_: MultiSourceExpectation[PRIMITIVE, OUTPUT],
            layouts: Sequence[NameAndValue[LayoutSpec]] = layout.STANDARD_LAYOUT_SPECS,
            sub_test_identifiers: Mapping[str, Any] = MappingProxyType({}),
    ):
        tokens = source.tokenization()
        for layout_case in layouts:
            source_str = tokens.layout(layout_case.value)
            for source_case in mk_source_variants(source_str):
                with put.subTest(_layout=layout_case.name,
                                 _source_variant=source_case.name,
                                 **sub_test_identifiers):
                    self._check__parse_source(
                        put,
                        source_case.source,
                        input_,
                        arrangement,
                        source_case.expectation,
                        expectation_,
                    )

    def check__abs_stx__layouts__source_variants__wo_input(
            self,
            put: unittest.TestCase,
            mk_source_variants: SourceStr2SourceVariants,
            source: AbstractSyntax,
            arrangement: Arrangement,
            expectation_: MultiSourceExpectation[PRIMITIVE, OUTPUT],
            layouts: Sequence[NameAndValue[LayoutSpec]] = layout.STANDARD_LAYOUT_SPECS,
            sub_test_identifiers: Mapping[str, Any] = MappingProxyType({}),
    ):
        self.check__abs_stx__layouts__source_variants(
            put,
            mk_source_variants,
            source,
            None,
            arrangement,
            expectation_,
            layouts,
            sub_test_identifiers,
        )

    def check__abs_stx__layout__std_source_variants(
            self,
            put: unittest.TestCase,
            source: AbstractSyntax,
            input_: INPUT,
            arrangement: Arrangement,
            expectation_: MultiSourceExpectation[PRIMITIVE, OUTPUT],
            layouts: Sequence[NameAndValue[LayoutSpec]] = layout.STANDARD_LAYOUT_SPECS,
            sub_test_identifiers: Mapping[str, Any] = MappingProxyType({}),
    ):
        self.check__abs_stx__layouts__source_variants(
            put,
            equivalent_source_variants__for_expr_parse__s__nsc,
            source,
            input_,
            arrangement,
            expectation_,
            layouts,
            sub_test_identifiers,
        )

    def check__abs_stx__layouts__std_source_variants__wo_input(
            self,
            put: unittest.TestCase,
            source: AbstractSyntax,
            arrangement: Arrangement,
            expectation_: MultiSourceExpectation[PRIMITIVE, OUTPUT],
            layouts: Sequence[NameAndValue[LayoutSpec]] = layout.STANDARD_LAYOUT_SPECS,
            sub_test_identifiers: Mapping[str, Any] = MappingProxyType({}),
    ):
        self.check__abs_stx__layout__std_source_variants(
            put,
            source,
            None,
            arrangement,
            expectation_,
            layouts,
            sub_test_identifiers,
        )

    def _check__parse_source(
            self,
            put: unittest.TestCase,
            parse_source: ParseSource,
            input_: INPUT,
            arrangement: Arrangement,
            expectation__source: Assertion[ParseSource],
            expectation_: MultiSourceExpectation[PRIMITIVE, OUTPUT],
    ):
        # ACT #
        actual = self._parser.parse(parse_source)
        # ASSERT #
        expectation__source.apply_with_message(put, parse_source, 'source after parse')
        self._check_sdv(put, actual, expectation_.symbol_references)

        checker = ExecutionChecker(put,
                                   input_,
                                   arrangement,
                                   expectation_.adv,
                                   expectation_.primitive,
                                   expectation_.execution,
                                   self._configuration.applier(),
                                   self._configuration.new_execution_checker(),
                                   self._check_application_result_with_tcds,
                                   )
        # ACT & ASSERT #
        checker.check(actual)

    def check__w_source_variants(self,
                                 put: unittest.TestCase,
                                 arguments: Arguments,
                                 input_: INPUT,
                                 arrangement: Arrangement,
                                 expectation: Expectation[PRIMITIVE, OUTPUT],
                                 ):
        for source in equivalent_source_variants__for_expression_parser(
                put, arguments):
            self.check(put, source, input_, arrangement, expectation)

    def check__w_source_variants_for_full_line_parser_2(self,
                                                        put: unittest.TestCase,
                                                        arguments: Arguments,
                                                        input_: INPUT,
                                                        arrangement: Arrangement,
                                                        expectation: Expectation[PRIMITIVE, OUTPUT],
                                                        ):
        self.check__w_source_variants_for_full_line_parser(
            put,
            arguments,
            input_,
            arrangement,
            MultiSourceExpectation(
                expectation.parse.symbol_references,
                expectation.execution,
                expectation.primitive,
            )
        )

    def check__w_source_variants_for_full_line_parser(self,
                                                      put: unittest.TestCase,
                                                      arguments: Arguments,
                                                      input_: INPUT,
                                                      arrangement: Arrangement,
                                                      expectation: MultiSourceExpectation[PRIMITIVE, OUTPUT]
                                                      ):
        checker = ExecutionChecker(put,
                                   input_,
                                   arrangement,
                                   expectation.adv,
                                   expectation.primitive,
                                   expectation.execution,
                                   self._configuration.applier(),
                                   self._configuration.new_execution_checker(),
                                   self._check_application_result_with_tcds,
                                   )
        for case in equivalent_source_variants__with_source_check__for_full_line_expression_parser(arguments):
            with put.subTest(case.name):
                source = case.actual

                actual_sdv = self._parser.parse(source)

                case.expected.apply_with_message(put, source, 'source after parse')
                self._check_sdv(put, actual_sdv, expectation.symbol_references)

                checker.check(actual_sdv)

    def check_multi(self,
                    put: unittest.TestCase,
                    arguments: Arguments,
                    parse_expectation: ParseExpectation,
                    input_: INPUT,
                    execution: Sequence[NExArr[PrimAndExeExpectation[PRIMITIVE, OUTPUT],
                                               Arrangement]],
                    ):
        source = arguments.as_remaining_source
        actual = self._parser.parse(source)
        parse_expectation.source.apply_with_message(put, source, 'source after parse')
        self._check_sdv(put, actual, parse_expectation.symbol_references)

        for case in execution:
            with put.subTest(case.name):
                checker = ExecutionChecker(put,
                                           input_,
                                           case.arrangement,
                                           case.expected.adv,
                                           case.expected.primitive,
                                           case.expected.execution,
                                           self._configuration.applier(),
                                           self._configuration.new_execution_checker(),
                                           self._check_application_result_with_tcds,
                                           )
                checker.check(actual)

    def check_multi__w_source_variants(self,
                                       put: unittest.TestCase,
                                       arguments: Arguments,
                                       symbol_references: Assertion[Sequence[SymbolReference]],
                                       input_: INPUT,
                                       execution: Sequence[NExArr[PrimAndExeExpectation[PRIMITIVE, OUTPUT],
                                                                  Arrangement]],
                                       ):
        self._check_multi__w_source_variants(
            put,
            symbol_references,
            input_,
            equivalent_source_variants__for_expression_parser_2(arguments),
            execution,
        )

    def check_multi__w_source_variants_for_full_line_parser(
            self,
            put: unittest.TestCase,
            arguments: Arguments,
            input_: INPUT,
            symbol_references: Assertion[Sequence[SymbolReference]],
            execution: Sequence[NExArr[PrimAndExeExpectation[PRIMITIVE, OUTPUT],
                                       Arrangement]],
    ):
        self._check_multi__w_source_variants(
            put,
            symbol_references,
            input_,
            equivalent_source_variants__with_source_check__for_full_line_expression_parser(arguments),
            execution,
        )

    def check_single_multi_execution_setup__for_test_of_test_resources(
            self,
            put: unittest.TestCase,
            arguments: Arguments,
            parse_expectation: ParseExpectation,
            model_constructor: INPUT,
            execution: NExArr[PrimAndExeExpectation[PRIMITIVE, OUTPUT], Arrangement],
    ):
        source = arguments.as_remaining_source
        actual = self._parser.parse(source)
        parse_expectation.source.apply_with_message(put, source, 'source after parse')

        self._check_sdv(put, actual, parse_expectation.symbol_references)

        checker = ExecutionChecker(put,
                                   model_constructor,
                                   execution.arrangement,
                                   execution.expected.adv,
                                   execution.expected.primitive,
                                   execution.expected.execution,
                                   self._configuration.applier(),
                                   self._configuration.new_execution_checker(),
                                   self._check_application_result_with_tcds,
                                   )
        checker.check(actual)

    def _check_multi__w_source_variants(
            self,
            put: unittest.TestCase,
            symbol_references: Assertion[Sequence[SymbolReference]],
            input_: INPUT,
            source_cases: Sequence[NEA[Assertion[ParseSource], ParseSource]],
            execution: Sequence[NExArr[PrimAndExeExpectation[PRIMITIVE, OUTPUT],
                                       Arrangement]],
    ):
        for source_case in source_cases:
            with put.subTest(source_case.name):
                source = source_case.actual
                actual = self._parser.parse(source)
                source_case.expected.apply_with_message(put, source, 'source after parse')
                self._check_sdv(put, actual, symbol_references)

                for case in execution:
                    with put.subTest(source_case=source_case.name,
                                     execution_case=case.name):
                        checker = ExecutionChecker(put,
                                                   input_,
                                                   case.arrangement,
                                                   case.expected.adv,
                                                   case.expected.primitive,
                                                   case.expected.execution,
                                                   self._configuration.applier(),
                                                   self._configuration.new_execution_checker(),
                                                   self._check_application_result_with_tcds,
                                                   )
                        checker.check(actual)

    def _check_sdv(self,
                   put: unittest.TestCase,
                   parsed_object,
                   symbol_references: Assertion[Sequence[SymbolReference]],
                   ):
        message_builder = asrt.MessageBuilder('parsed object')
        asrt.is_instance(FullDepsSdv).apply(put,
                                            parsed_object,
                                            message_builder.for_sub_component('object type'))

        assert isinstance(parsed_object, FullDepsSdv)  # Type info for IDE

        self._configuration.new_sdv_checker().check(put,
                                                    parsed_object,
                                                    message_builder)
        symbol_references.apply(put,
                                parsed_object.references,
                                message_builder.for_sub_component('symbol references'))


class _ParseAndExecutionChecker(Generic[PRIMITIVE, INPUT, OUTPUT]):
    FAKE_TCDS = fake_tcds()

    def __init__(self,
                 put: unittest.TestCase,
                 model_constructor: INPUT,
                 parser: Parser[FullDepsSdv[PRIMITIVE]],
                 arrangement: Arrangement,
                 configuration: CommonPropertiesConfiguration[PRIMITIVE, INPUT, OUTPUT],
                 check_application_result_with_tcds: bool,
                 expectation: Expectation[PRIMITIVE, OUTPUT],
                 ):
        self.put = put
        self.parser = parser
        self.configuration = configuration
        self.expectation = expectation
        self.source_expectation = expectation.parse.source
        self._execution_checker = ExecutionChecker(put,
                                                   model_constructor,
                                                   arrangement,
                                                   expectation.adv,
                                                   expectation.primitive,
                                                   expectation.execution,
                                                   configuration.applier(),
                                                   configuration.new_execution_checker(),
                                                   check_application_result_with_tcds,
                                                   )

    def check(self, source: ParseSource):
        matcher_sdv = self._parse(source)
        self._execution_checker.check(matcher_sdv)

    def _parse(self, source: ParseSource) -> FullDepsSdv[PRIMITIVE]:
        sdv = self.parser.parse(source)

        self.source_expectation.apply_with_message(
            self.put,
            source,
            'source after parse',
        )

        message_builder = asrt.MessageBuilder('parsed object')

        self.expectation.parse.symbol_references.apply(
            self.put,
            sdv.references,
            message_builder.for_sub_component('symbol references'),
        )
        self.configuration.new_sdv_checker().check(
            self.put,
            sdv,
            message_builder,
        )
        return sdv
