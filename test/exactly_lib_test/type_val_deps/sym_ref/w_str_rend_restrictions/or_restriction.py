import unittest

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.symbol.sdv_structure import SymbolContainer, SymbolDependentValue
from exactly_lib.symbol.value_type import WithStrRenderingType, ValueType, W_STR_RENDERING_TYPE_2_VALUE_TYPE
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions import reference_restrictions as sut
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.sym_ref.w_str_rend_restrictions.test_resources import TestDataSymbolContext, \
    reference_to
from exactly_lib_test.type_val_deps.test_resources.w_str_rend.data_restrictions_assertions import \
    is_failure__of_direct_reference, is_failure__of_indirect_reference
from exactly_lib_test.type_val_deps.test_resources.w_str_rend.value_restrictions import \
    ValueRestrictionWithConstantResult, \
    ValueRestrictionThatRaisesErrorIfApplied
from exactly_lib_test.type_val_deps.types.string_transformer.test_resources.string_transformers import \
    StringTransformerSdvConstantTestImpl
from exactly_lib_test.type_val_deps.types.string_transformer.test_resources.symbol_context import \
    StringTransformerSymbolContext
from exactly_lib_test.type_val_prims.string_transformer.test_resources import string_transformers


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestOrReferenceRestrictions),
    ])


class TestOrReferenceRestrictions(unittest.TestCase):
    def test_satisfied(self):
        cases = [
            NameAndValue(
                'single satisfied string-selector restriction, unconditionally satisfied part',
                sut.OrReferenceRestrictions([
                    sut.OrRestrictionPart(WithStrRenderingType.STRING,
                                          sut.ReferenceRestrictionsOnDirectAndIndirect(
                                              direct=ValueRestrictionWithConstantResult.of_unconditionally_satisfied()))
                ])
            ),
            NameAndValue(
                'multiple unconditionally satisfied restrictions',
                sut.OrReferenceRestrictions([
                    sut.OrRestrictionPart(WithStrRenderingType.STRING,
                                          sut.ReferenceRestrictionsOnDirectAndIndirect(
                                              direct=ValueRestrictionWithConstantResult.of_unconditionally_satisfied())),
                    sut.OrRestrictionPart(WithStrRenderingType.STRING,
                                          sut.ReferenceRestrictionsOnDirectAndIndirect(
                                              direct=ValueRestrictionWithConstantResult.of_unconditionally_satisfied()))
                ])
            ),
        ]
        for case in cases:
            with self.subTest(msg=case.name):
                actual = case.value.is_satisfied_by(*self._symbol_setup_with_indirectly_referenced_symbol())
                self.assertIsNone(actual)

    def test_unsatisfied(self):

        def mk_err_msg(symbol_name: str,
                       value_type: ValueType) -> str:
            return symbol_name + ': ' + 'Value type of tested symbol is ' + str(value_type)

        def value_type_error_message_function(symbol_name: str,
                                              container: SymbolContainer) -> TextRenderer:
            sdv = container.sdv
            assert isinstance(sdv, SymbolDependentValue)  # Type info for IDE
            return asrt_text_doc.new_single_string_text_for_test(mk_err_msg(symbol_name, container.value_type))

        references = []
        referenced_symbol_cases = [
            NameAndValue(
                'data symbol',
                TestDataSymbolContext.of('referenced_data_symbol', references, WithStrRenderingType.STRING)
            ),
            NameAndValue(
                'logic symbol',
                StringTransformerSymbolContext.of_sdv('referenced_logic_symbol',
                                                      StringTransformerSdvConstantTestImpl(
                                                          string_transformers.arbitrary(),
                                                          references=[]))
            ),
        ]
        for referenced_symbol_case in referenced_symbol_cases:
            restrictions_that_should_not_be_used = sut.ReferenceRestrictionsOnDirectAndIndirect(
                direct=ValueRestrictionThatRaisesErrorIfApplied(),
                indirect=ValueRestrictionThatRaisesErrorIfApplied(),
            )

            value_type_of_referencing_symbol = WithStrRenderingType.STRING
            value_type_other_than_referencing_symbol = WithStrRenderingType.PATH

            references1 = [reference_to(referenced_symbol_case.value,
                                        restrictions_that_should_not_be_used)]
            referencing_symbol = TestDataSymbolContext.of('referencing_symbol', references1,
                                                          value_type_of_referencing_symbol)
            symbol_table_entries = [referencing_symbol, referenced_symbol_case.value]

            symbol_table = SymbolContext.symbol_table_of_contexts(symbol_table_entries)
            cases = [
                NEA('no restriction parts / default error message generator',
                    is_failure__of_direct_reference(),
                    sut.OrReferenceRestrictions([]),
                    ),
                NEA('no restriction parts / custom error message generator',
                    is_failure__of_direct_reference(
                        message=asrt_text_doc.is_string_for_test_that_equals(
                            mk_err_msg(referencing_symbol.name,
                                       W_STR_RENDERING_TYPE_2_VALUE_TYPE[value_type_of_referencing_symbol])
                        ),
                    ),
                    sut.OrReferenceRestrictions([], value_type_error_message_function),
                    ),
                NEA('single direct: unsatisfied selector',
                    is_failure__of_direct_reference(),
                    sut.OrReferenceRestrictions([
                        sut.OrRestrictionPart(value_type_other_than_referencing_symbol,
                                              sut.ReferenceRestrictionsOnDirectAndIndirect(
                                                  direct=ValueRestrictionWithConstantResult.of_unconditionally_satisfied())),
                    ]),
                    ),
                NEA('single direct: satisfied selector, unsatisfied part-restriction',
                    is_failure__of_direct_reference(),
                    sut.OrReferenceRestrictions([
                        sut.OrRestrictionPart(value_type_of_referencing_symbol,
                                              sut.ReferenceRestrictionsOnDirectAndIndirect(
                                                  direct=ValueRestrictionWithConstantResult.of_err_msg_for_test(
                                                      'error message'))),
                    ]),
                    ),
                NEA('multiple direct: unconditionally unsatisfied selectors',
                    is_failure__of_direct_reference(),
                    sut.OrReferenceRestrictions([
                        sut.OrRestrictionPart(
                            value_type_other_than_referencing_symbol,
                            sut.ReferenceRestrictionsOnDirectAndIndirect(
                                direct=ValueRestrictionWithConstantResult.of_err_msg_for_test('error message'))),
                        sut.OrRestrictionPart(
                            value_type_other_than_referencing_symbol,
                            sut.ReferenceRestrictionsOnDirectAndIndirect(
                                direct=ValueRestrictionWithConstantResult.of_err_msg_for_test('error message')))
                    ]),
                    ),
                NEA('multiple direct: unconditionally satisfied selectors, unconditionally satisfied restrictions',
                    is_failure__of_direct_reference(),
                    sut.OrReferenceRestrictions([
                        sut.OrRestrictionPart(
                            value_type_of_referencing_symbol,
                            sut.ReferenceRestrictionsOnDirectAndIndirect(
                                direct=ValueRestrictionWithConstantResult.of_err_msg_for_test('error message'))),
                        sut.OrRestrictionPart(
                            value_type_of_referencing_symbol,
                            sut.ReferenceRestrictionsOnDirectAndIndirect(
                                direct=ValueRestrictionWithConstantResult.of_err_msg_for_test('error message')))
                    ]),
                    ),
                NEA('first: selector=satisfied, direct=satisfied, indirect=unsatisfied. second:satisfied ',
                    is_failure__of_indirect_reference(
                        failing_symbol=asrt.equals(referenced_symbol_case.value.name),
                        path_to_failing_symbol=asrt.equals([])),
                    sut.OrReferenceRestrictions([
                        sut.OrRestrictionPart(
                            value_type_of_referencing_symbol,
                            sut.ReferenceRestrictionsOnDirectAndIndirect(
                                direct=ValueRestrictionWithConstantResult.of_unconditionally_satisfied(),
                                indirect=ValueRestrictionWithConstantResult.of_err_msg_for_test('error message'))),
                        sut.OrRestrictionPart(
                            value_type_of_referencing_symbol,
                            sut.ReferenceRestrictionsOnDirectAndIndirect(
                                direct=ValueRestrictionWithConstantResult.of_unconditionally_satisfied())),
                    ]),
                    ),
            ]

            for case in cases:
                with self.subTest(referenced_symbol_case_name=referenced_symbol_case.name,
                                  msg=case.name):
                    actual = case.actual.is_satisfied_by(symbol_table,
                                                         referencing_symbol.name,
                                                         referencing_symbol.symbol_table_container)
                    case.expected.apply_with_message(self, actual, 'return value')

    @staticmethod
    def _symbol_setup_with_indirectly_referenced_symbol():
        references = []
        referenced_symbol = TestDataSymbolContext.of('referenced_symbol', references, WithStrRenderingType.STRING)
        restrictions_that_should_not_be_used = sut.ReferenceRestrictionsOnDirectAndIndirect(
            direct=ValueRestrictionThatRaisesErrorIfApplied(),
            indirect=ValueRestrictionThatRaisesErrorIfApplied(),
        )

        references1 = [reference_to(referenced_symbol,
                                    restrictions_that_should_not_be_used)]
        referencing_symbol = TestDataSymbolContext.of('referencing_symbol', references1, WithStrRenderingType.STRING)
        symbol_table_entries = [referencing_symbol, referenced_symbol]

        symbol_table = SymbolContext.symbol_table_of_contexts(symbol_table_entries)

        return symbol_table, referencing_symbol.name, referencing_symbol.symbol_table_container,


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
