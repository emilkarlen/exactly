import unittest

from exactly_lib.help_texts import expression
from exactly_lib.named_element.resolver_structure import NamedElementResolver, NamedElementContainer
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parser_implementations.token_stream_parse_prime import TokenParserPrime
from exactly_lib.type_system.logic.matcher_base_class import Matcher
from exactly_lib.util import symbol_table
from exactly_lib.util.symbol_table import singleton_symbol_table_2, SymbolTable
from exactly_lib_test.named_element.test_resources.named_elem_utils import container
from exactly_lib_test.section_document.parser_implementations.test_resources.token_stream_parser_prime \
    import remaining_source
from exactly_lib_test.test_case_utils.expression.test_resources import \
    NOT_A_SIMPLE_EXPR_NAME_AND_NOT_A_VALID_SYMBOL_NAME
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


class Configuration:
    def parse(self, parser: TokenParserPrime) -> NamedElementResolver:
        raise NotImplementedError('abstract method')

    def resolved_value_equals(self, value: Matcher,
                              references: asrt.ValueAssertion = asrt.is_empty_list,
                              symbols: symbol_table.SymbolTable = None) -> asrt.ValueAssertion:
        raise NotImplementedError('abstract method')

    def is_reference_to(self, symbol_name: str) -> asrt.ValueAssertion:
        raise NotImplementedError('abstract method')

    def resolver_of_constant_matcher(self, matcher: Matcher) -> NamedElementResolver:
        raise NotImplementedError('abstract method')

    def container_with_resolver_of_constant_matcher(self, matcher: Matcher) -> NamedElementContainer:
        return container(self.resolver_of_constant_matcher(matcher))

    def constant_matcher(self, result: bool) -> Matcher:
        raise NotImplementedError('abstract method')

    def not_matcher(self, matcher: Matcher) -> Matcher:
        raise NotImplementedError('abstract method')

    def and_matcher(self, matchers: list) -> Matcher:
        raise NotImplementedError('abstract method')

    def or_matcher(self, matchers: list) -> Matcher:
        raise NotImplementedError('abstract method')


class Expectation:
    def __init__(self,
                 resolver: asrt.ValueAssertion,
                 token_stream: asrt.ValueAssertion = asrt.anything_goes()):
        self.resolver = resolver
        self.token_stream = token_stream


class TestParseStandardExpressionsBase(unittest.TestCase):
    @property
    def conf(self) -> Configuration:
        raise NotImplementedError('abstract method')

    def _check(self,
               source: TokenParserPrime,
               expectation: Expectation):
        # ACT #
        actual_resolver = self.conf.parse(source)
        # ASSERT #
        expectation.resolver.apply_with_message(self,
                                                actual_resolver,
                                                'resolver')
        expectation.token_stream.apply_with_message(self,
                                                    source.token_stream,
                                                    'token stream')

    def test_failing_parse(self):
        cases = [
            (
                'neither a symbol, nor a matcher',
                remaining_source(NOT_A_SIMPLE_EXPR_NAME_AND_NOT_A_VALID_SYMBOL_NAME),
            ),
        ]
        for name, source in cases:
            with self.subTest(case_name=name):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    self.conf.parse(source)

    def test_reference(self):
        # ARRANGE #
        conf = self.conf
        symbol = NameAndValue('the_symbol_name',
                              conf.constant_matcher(True))

        symbols = singleton_symbol_table_2(symbol.name,
                                           conf.container_with_resolver_of_constant_matcher(symbol.value))

        # ACT & ASSERT #
        self._check(
            remaining_source(symbol.name),
            Expectation(
                resolver=conf.resolved_value_equals(
                    value=symbol.value,
                    references=asrt.matches_sequence([conf.is_reference_to(symbol.name)]),
                    symbols=symbols
                ),
            ))

    def test_not(self):
        # ARRANGE #
        conf = self.conf
        symbol = NameAndValue('the_symbol_name',
                              conf.constant_matcher(True))

        symbols = singleton_symbol_table_2(symbol.name,
                                           conf.container_with_resolver_of_constant_matcher(symbol.value))

        # ACT & ASSERT #
        self._check(
            remaining_source('{not_} {symbol}'.format(not_=expression.NOT_OPERATOR_NAME,
                                                      symbol=symbol.name)),
            Expectation(
                resolver=conf.resolved_value_equals(
                    value=conf.not_matcher(symbol.value),
                    references=asrt.matches_sequence([conf.is_reference_to(symbol.name)]),
                    symbols=symbols
                ),
            ))

    def test_and(self):
        # ARRANGE #
        conf = self.conf
        symbol_1 = NameAndValue('the_symbol_1_name',
                                conf.constant_matcher(True))

        symbol_2 = NameAndValue('the_symbol_2_name',
                                conf.constant_matcher(False))

        symbols = SymbolTable({
            symbol_1.name: conf.container_with_resolver_of_constant_matcher(symbol_1.value),
            symbol_2.name: conf.container_with_resolver_of_constant_matcher(symbol_2.value),
        })

        # ACT & ASSERT #
        self._check(
            remaining_source('{symbol_1} {and_op} {symbol_2}'.format(
                symbol_1=symbol_1.name,
                and_op=expression.AND_OPERATOR_NAME,
                symbol_2=symbol_2.name,
            )),
            Expectation(
                resolver=conf.resolved_value_equals(
                    value=conf.and_matcher([symbol_1.value,
                                            symbol_2.value]),
                    references=asrt.matches_sequence([
                        conf.is_reference_to(symbol_1.name),
                        conf.is_reference_to(symbol_2.name),
                    ]),
                    symbols=symbols
                ),
            ))

    def test_or(self):
        # ARRANGE #
        conf = self.conf
        symbol_1 = NameAndValue('the_symbol_1_name',
                                conf.constant_matcher(True))

        symbol_2 = NameAndValue('the_symbol_2_name',
                                conf.constant_matcher(False))

        symbols = SymbolTable({
            symbol_1.name: conf.container_with_resolver_of_constant_matcher(symbol_1.value),
            symbol_2.name: conf.container_with_resolver_of_constant_matcher(symbol_2.value),
        })

        # ACT & ASSERT #
        self._check(
            remaining_source('{symbol_1} {or_op} {symbol_2}'.format(
                symbol_1=symbol_1.name,
                or_op=expression.OR_OPERATOR_NAME,
                symbol_2=symbol_2.name,
            )),
            Expectation(
                resolver=conf.resolved_value_equals(
                    value=conf.or_matcher([symbol_1.value,
                                           symbol_2.value]),
                    references=asrt.matches_sequence([
                        conf.is_reference_to(symbol_1.name),
                        conf.is_reference_to(symbol_2.name),
                    ]),
                    symbols=symbols
                ),
            ))
