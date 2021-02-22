import unittest
from typing import Optional

from exactly_lib.common.err_msg.err_msg_w_fix_tip import ErrorMessageWithFixTip
from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.symbol.sdv_structure import SymbolContainer
from exactly_lib.type_val_deps.sym_ref.data import reference_restrictions as sut
from exactly_lib.type_val_deps.sym_ref.data.data_value_restriction import ValueRestriction
from exactly_lib.type_val_deps.sym_ref.data.value_restrictions import AnyDataTypeRestriction, StringRestriction, \
    PathRelativityRestriction, ValueRestrictionVisitor
from exactly_lib.util.render.renderer import Renderer
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion, AssertionBase
from exactly_lib_test.type_val_deps.types.path.test_resources.path_relativity import equals_path_relativity_variants


def matches_value_restriction_failure(message: Assertion[TextRenderer]) -> Assertion[ErrorMessageWithFixTip]:
    return asrt.is_instance_with(
        ErrorMessageWithFixTip,
        asrt.and_([
            asrt.sub_component('message',
                               ErrorMessageWithFixTip.message.fget,
                               message),
            asrt.sub_component('how_to_fix',
                               ErrorMessageWithFixTip.how_to_fix.fget,
                               asrt.is_none_or_instance_with(Renderer, asrt_text_doc.is_any_text())),
        ])
    )


is_value_restriction__convertible_to_string = asrt.is_instance(AnyDataTypeRestriction)

is_value_restriction__string = asrt.is_instance(StringRestriction)


def equals_string_restriction(expected: StringRestriction) -> Assertion[ValueRestriction]:
    return is_value_restriction__string


def equals_path_relativity_restriction(expected: PathRelativityRestriction) -> Assertion[ValueRestriction]:
    return asrt.is_instance_with(PathRelativityRestriction,
                                 asrt.sub_component('accepted',
                                                    PathRelativityRestriction.accepted.fget,
                                                    equals_path_relativity_variants(expected.accepted)))


def equals_value_restriction(expected: ValueRestriction) -> Assertion[ValueRestriction]:
    return _EqualsValueRestriction(expected)


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


class _EqualsValueRestriction(AssertionBase[ValueRestriction]):
    def __init__(self, expected: ValueRestriction):
        self.expected = expected

    def _apply(self,
               put: unittest.TestCase,
               value,
               message_builder: asrt.MessageBuilder):
        _EqualsValueRestrictionVisitor(value, put, message_builder).visit(self.expected)


class _EqualsValueRestrictionVisitor(ValueRestrictionVisitor):
    def __init__(self,
                 actual,
                 put: unittest.TestCase,
                 message_builder: asrt.MessageBuilder):
        self.message_builder = message_builder
        self.actual = actual
        self.put = put

    def visit_none(self, expected: AnyDataTypeRestriction):
        is_value_restriction__convertible_to_string.apply(self.put, self.actual, self.message_builder)

    def visit_string(self, expected: StringRestriction):
        equals_string_restriction(expected).apply(self.put, self.actual, self.message_builder)

    def visit_path_relativity(self, expected: PathRelativityRestriction):
        equals_path_relativity_restriction(expected).apply(self.put, self.actual, self.message_builder)
