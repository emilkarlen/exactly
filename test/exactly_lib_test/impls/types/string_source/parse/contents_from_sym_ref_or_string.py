import unittest
from typing import Callable, List

from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.parse.token import QuoteType
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import arrangement_w_tcds, \
    AssertionResolvingEnvironment, MultiSourceExpectation
from exactly_lib_test.impls.types.string_source.test_resources import integration_check
from exactly_lib_test.impls.types.string_source.test_resources.abstract_syntaxes import StringSourceOfStringAbsStx, \
    TransformedStringSourceAbsStx
from exactly_lib_test.impls.types.string_source.test_resources.parse_check import ARBITRARY_FILE_RELATIVITIES
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.test_resources.w_str_rend import data_restrictions_assertions as asrt_rest
from exactly_lib_test.type_val_deps.types.list_.test_resources.symbol_context import ListSymbolContext
from exactly_lib_test.type_val_deps.types.path.test_resources.symbol_context import ConstantSuffixPathDdvSymbolContext
from exactly_lib_test.type_val_deps.types.string_.test_resources import list_formatting
from exactly_lib_test.type_val_deps.types.string_.test_resources.abstract_syntaxes import StringLiteralAbsStx
from exactly_lib_test.type_val_deps.types.string_.test_resources.symbol_context import StringConstantSymbolContext
from exactly_lib_test.type_val_deps.types.string_source.test_resources import references
from exactly_lib_test.type_val_deps.types.string_source.test_resources.abstract_syntax import \
    StringSourceSymbolReferenceAbsStx, TransformableStringSourceAbsStx
from exactly_lib_test.type_val_deps.types.string_source.test_resources.symbol_context import StringSourceSymbolContext
from exactly_lib_test.type_val_deps.types.string_transformer.test_resources.symbol_context import \
    StringTransformerSymbolContext
from exactly_lib_test.type_val_prims.string_source.test_resources import assertions as asrt_string_source
from exactly_lib_test.type_val_prims.string_transformer.test_resources import string_transformers


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestPlainSymbolReferences),
        unittest.makeSuite(TestStringWithReferences),
    ])


class Case:
    def __init__(self,
                 syntax: TransformableStringSourceAbsStx,
                 symbol: SymbolContext,
                 expectation_of_primitive: Callable[[AssertionResolvingEnvironment], Assertion[StringSource]],
                 ):
        self.syntax = syntax
        self.symbol = symbol
        self.expectation_of_primitive = expectation_of_primitive


class TestStringWithReferences(unittest.TestCase):
    def test_wo_transformation(self):
        # ARRANGE #
        cases: List[NameAndValue[Case]] = [
            NameAndValue('path (within soft quotes)', _path_case(_no_transformation)),
            NameAndValue('list (within soft quotes)', _list_case(_no_transformation)),
        ]

        for case in cases:
            # ACT & ASSERT #
            CHECKER.check__abs_stx__layouts__std_source_variants__wo_input(
                self,
                case.value.syntax,
                arrangement_w_tcds(
                    symbols=case.value.symbol.symbol_table,
                ),
                MultiSourceExpectation.of_prim(
                    symbol_references=asrt.matches_singleton_sequence(
                        references.is_reference_to__string(case.value.symbol.name)
                    ),
                    primitive=case.value.expectation_of_primitive,
                ),
                sub_test_identifiers={
                    'case': case.name,
                }
            )

    def test_w_transformation(self):
        str_added_by_transformer = '<string added by transformer>'
        transformer_symbol = StringTransformerSymbolContext.of_primitive(
            'TRANSFORMER',
            string_transformers.add(str_added_by_transformer),
        )

        def contents_transformation(s: str) -> str:
            return s + str_added_by_transformer

        # ARRANGE #
        cases: List[NameAndValue[Case]] = [
            NameAndValue('path (within soft quotes)', _path_case(contents_transformation)),
            NameAndValue('list (within soft quotes)', _list_case(contents_transformation)),
        ]

        for case in cases:
            syntax = TransformedStringSourceAbsStx(
                case.value.syntax,
                transformer_symbol.abstract_syntax,
            )
            all_symbols = [case.value.symbol, transformer_symbol]
            # ACT & ASSERT #
            CHECKER.check__abs_stx__layouts__std_source_variants__wo_input(
                self,
                syntax,
                arrangement_w_tcds(
                    symbols=SymbolContext.symbol_table_of_contexts(all_symbols),
                ),
                MultiSourceExpectation.of_prim(
                    symbol_references=asrt.matches_sequence([
                        references.is_reference_to__string(case.value.symbol.name),
                        transformer_symbol.reference_assertion,
                    ]),
                    primitive=case.value.expectation_of_primitive,
                ),
                sub_test_identifiers={
                    'case': case.name,
                }
            )


class TestPlainSymbolReferences(unittest.TestCase):
    def test_wo_transformation(self):
        # ARRANGE #
        cases: List[NameAndValue[Case]] = [
            NameAndValue('string', _string_case(_no_transformation)),
            NameAndValue('string-source', _string_source_case(_no_transformation)),
        ]

        for case in cases:
            # ACT & ASSERT #
            CHECKER.check__abs_stx__layouts__std_source_variants__wo_input(
                self,
                case.value.syntax,
                arrangement_w_tcds(
                    symbols=case.value.symbol.symbol_table,
                ),
                MultiSourceExpectation.of_prim(
                    symbol_references=asrt.matches_singleton_sequence(
                        references.is_reference_to__string_source_or_string(case.value.symbol.name)
                    ),
                    primitive=case.value.expectation_of_primitive,
                ),
                sub_test_identifiers={
                    'case': case.name,
                }
            )

    def test_w_transformation(self):
        # ARRANGE #
        str_added_by_transformer = '<string added by transformer>'
        transformer_symbol = StringTransformerSymbolContext.of_primitive(
            'TRANSFORMER',
            string_transformers.add(str_added_by_transformer),
        )

        def contents_transformation(s: str) -> str:
            return s + str_added_by_transformer

        cases: List[NameAndValue[Case]] = [
            NameAndValue('string', _string_case(contents_transformation)),
            NameAndValue('string-source', _string_source_case(contents_transformation)),
        ]

        for case in cases:
            syntax = TransformedStringSourceAbsStx(
                case.value.syntax,
                transformer_symbol.abstract_syntax,
            )
            all_symbols = [case.value.symbol, transformer_symbol]
            # ACT & ASSERT #
            CHECKER.check__abs_stx__layouts__std_source_variants__wo_input(
                self,
                syntax,
                arrangement_w_tcds(
                    symbols=SymbolContext.symbol_table_of_contexts(all_symbols),
                ),
                MultiSourceExpectation.of_prim(
                    symbol_references=asrt.matches_sequence([
                        references.is_reference_to__string_source_or_string(case.value.symbol.name),
                        transformer_symbol.reference_assertion,
                    ]),
                    primitive=case.value.expectation_of_primitive,
                ),
                sub_test_identifiers={
                    'case': case.name,
                }
            )


def _string_case(contents_transformation: Callable[[str], str]) -> Case:
    string_contents = 'the value of the string symbol'

    def get_assertion_on_primitive(env: AssertionResolvingEnvironment) -> Assertion[StringSource]:
        return asrt_string_source.pre_post_freeze__matches_str__const(
            contents_transformation(string_contents),
            may_depend_on_external_resources=False)

    symbol_context = StringConstantSymbolContext(
        'STRING_SYMBOL', string_contents,
        default_restrictions=asrt_rest.is__w_str_rendering(),
    )
    return Case(
        StringSourceSymbolReferenceAbsStx(symbol_context.name),
        symbol_context,
        get_assertion_on_primitive,
    )


def _path_case(contents_transformation: Callable[[str], str]) -> Case:
    relativity = RelOptionType.REL_TMP
    path_suffix = 'the path suffix'

    def get_assertion_on_primitive(env: AssertionResolvingEnvironment) -> Assertion[StringSource]:
        path_as_str = str(env.tcds.sds.user_tmp_dir / path_suffix)
        return asrt_string_source.pre_post_freeze__matches_str__const(
            contents_transformation(path_as_str),
            may_depend_on_external_resources=False)

    symbol_context = ConstantSuffixPathDdvSymbolContext(
        'PATH_SYMBOL',
        relativity, path_suffix,
        ARBITRARY_FILE_RELATIVITIES.accepted_relativity_variants,
    )
    return Case(
        StringSourceOfStringAbsStx(
            StringLiteralAbsStx(symbol_context.name__sym_ref_syntax, QuoteType.SOFT)
        ),
        symbol_context,
        get_assertion_on_primitive,
    )


def _list_case(contents_transformation: Callable[[str], str]) -> Case:
    elements = ['1st element', '2nd element']

    def get_assertion_on_primitive(env: AssertionResolvingEnvironment) -> Assertion[StringSource]:
        list_as_str = list_formatting.format_elements(elements)
        return asrt_string_source.pre_post_freeze__matches_str__const(
            contents_transformation(list_as_str),
            may_depend_on_external_resources=False)

    symbol_context = ListSymbolContext.of_constants('LIST_SYMBOL', elements)

    return Case(
        StringSourceOfStringAbsStx(
            StringLiteralAbsStx(symbol_context.name__sym_ref_syntax, QuoteType.SOFT)
        ),
        symbol_context,
        get_assertion_on_primitive,
    )


def _string_source_case(contents_transformation: Callable[[str], str]) -> Case:
    string_source_contents = 'the value of the string symbol'

    def get_assertion_on_primitive(env: AssertionResolvingEnvironment) -> Assertion[StringSource]:
        return asrt_string_source.pre_post_freeze__matches_str__const(
            contents_transformation(string_source_contents),
            may_depend_on_external_resources=False)

    symbol_context = StringSourceSymbolContext.of_primitive_constant(
        'STRING_SOURCE_SYMBOL',
        string_source_contents,
    )
    return Case(
        StringSourceSymbolReferenceAbsStx(symbol_context.name),
        symbol_context,
        get_assertion_on_primitive,
    )


def _no_transformation(s: str) -> str:
    return s


CHECKER = integration_check.checker__w_arbitrary_file_relativities()
