import unittest
from types import MappingProxyType
from typing import TypeVar, Generic, Optional, Sequence, Mapping, Any

from exactly_lib.section_document.element_parsers import token_stream_parser
from exactly_lib.section_document.element_parsers.token_stream_parser import ParserFromTokens
from exactly_lib.symbol.sdv_structure import SymbolReference, TypedSymbolDependentValue
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.impls.types.parse.test_resources import \
    single_line_source_instruction_utils as equivalent_source_variants
from exactly_lib_test.test_resources.source import abs_stx_utils
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion

T = TypeVar('T')


class Expectation(Generic[T]):
    def __init__(self,
                 symbol_references: Assertion[Sequence[SymbolReference]],
                 sdv: Assertion[TypedSymbolDependentValue[T]],
                 ddv: Assertion[T],
                 ):
        self.symbol_references = symbol_references
        self.sdv = sdv
        self.ddv = ddv


class Checker(Generic[T]):
    def __init__(self, parser: ParserFromTokens[TypedSymbolDependentValue[T]]):
        self._parser = parser

    def check__abs_stx__expr_parse_source_variants(
            self,
            put: unittest.TestCase,
            syntax: AbstractSyntax,
            symbols: Optional[SymbolTable],
            expectation: Expectation[T],
            sub_test_identifiers: Mapping[str, Any] = MappingProxyType({}),
    ):
        if symbols is None:
            symbols = SymbolTable.empty()
        for formatting_case in abs_stx_utils.formatting_cases(syntax):
            for equivalent_source_case in equivalent_source_variants.expr_parse__s__nsc(formatting_case.value):
                with put.subTest(zz_formatting=formatting_case.name,
                                 zz_following_source_variant=equivalent_source_case.name,
                                 **sub_test_identifiers):
                    parse_source = equivalent_source_case.source
                    with token_stream_parser.from_parse_source(parse_source) as token_parser:
                        # ACT
                        sdv = self._parser.parse(token_parser)
                    # ASSERT #
                    equivalent_source_case.expectation.apply_with_message(
                        put,
                        parse_source,
                        'source after parse',
                    )
                    expectation.symbol_references.apply_with_message(
                        put,
                        sdv.references,
                        'symbol references',
                    )
                    expectation.sdv.apply_with_message(
                        put,
                        sdv,
                        'custom sdv expectation'
                    )
                    # ACT #
                    ddv = sdv.resolve(symbols)
                    # ASSERT #
                    expectation.ddv.apply_with_message(
                        put,
                        ddv,
                        'ddv',
                    )
