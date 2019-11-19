from typing import Optional

from exactly_lib.symbol import sdv_structure as vs
from exactly_lib.symbol.data.restrictions.reference_restrictions import \
    ReferenceRestrictionsOnDirectAndIndirect
from exactly_lib.symbol.data.restrictions.value_restrictions import AnyDataTypeRestriction, StringRestriction
from exactly_lib.symbol.data.value_restriction import ErrorMessageWithFixTip, ValueRestriction
from exactly_lib.symbol.restriction import ReferenceRestrictions
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc


class RestrictionThatCannotBeSatisfied(ValueRestriction):
    def is_satisfied_by(self,
                        symbol_table: vs.SymbolTable,
                        symbol_name: str,
                        container: vs.SymbolContainer) -> Optional[ErrorMessageWithFixTip]:
        return ErrorMessageWithFixTip(
            asrt_text_doc.new_single_string_text_for_test('unconditional error')
        )


def unconditionally_satisfied_reference_restrictions() -> ReferenceRestrictions:
    return ReferenceRestrictionsOnDirectAndIndirect(AnyDataTypeRestriction())


def unconditionally_unsatisfied_reference_restrictions() -> ReferenceRestrictions:
    return ReferenceRestrictionsOnDirectAndIndirect(RestrictionThatCannotBeSatisfied())


def string_made_up_of_just_strings_reference_restrictions() -> ReferenceRestrictionsOnDirectAndIndirect:
    return ReferenceRestrictionsOnDirectAndIndirect(StringRestriction(),
                                                    StringRestriction())
