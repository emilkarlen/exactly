from typing import Optional

from exactly_lib.common.err_msg.err_msg_w_fix_tip import ErrorMessageWithFixTip
from exactly_lib.symbol.sdv_structure import SymbolContainer
from exactly_lib.symbol.value_type import WithStrRenderingType
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions import reference_restrictions as sut
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions.data_value_restriction import ValueRestriction
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions.value_restrictions import \
    ArbitraryValueWStrRenderingRestriction
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc


def is_string() -> ValueRestriction:
    return ArbitraryValueWStrRenderingRestriction.of_single(WithStrRenderingType.STRING)


class ValueRestrictionWithConstantResult(ValueRestriction):
    def __init__(self, result: Optional[ErrorMessageWithFixTip]):
        self.result = result

    @staticmethod
    def of_unconditionally_satisfied() -> ValueRestriction:
        return ValueRestrictionWithConstantResult(None)

    @staticmethod
    def of_err_msg_for_test(error_message: str = 'unconditional error') -> ValueRestriction:
        return ValueRestrictionWithConstantResult(
            ErrorMessageWithFixTip(
                asrt_text_doc.new_single_string_text_for_test(error_message))
        )

    def is_satisfied_by(self,
                        symbol_table: SymbolTable,
                        symbol_name: str,
                        container: SymbolContainer) -> Optional[ErrorMessageWithFixTip]:
        return self.result


class ValueRestrictionThatRaisesErrorIfApplied(ValueRestriction):
    def is_satisfied_by(self,
                        symbol_table: SymbolTable,
                        symbol_name: str,
                        value: sut.SymbolContainer) -> Optional[ErrorMessageWithFixTip]:
        raise NotImplementedError('It is an error if this method is called')
