import unittest
from typing import Sequence

from exactly_lib.common.err_msg.err_msg_w_fix_tip import ErrorMessageWithFixTip
from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.symbol import value_type
from exactly_lib.symbol.value_type import WithStrRenderingType
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions.data_value_restriction import ValueRestriction
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions.value_restrictions import \
    ArbitraryValueWStrRenderingRestriction, \
    PathAndRelativityRestriction
from exactly_lib_test.common.err_msg.test_resources import err_msg_w_fix_tip
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion, AssertionBase, MessageBuilder
from exactly_lib_test.type_val_deps.test_resources.w_str_rend.value_restrictions_visitor import \
    ProdValueRestrictionVariantsVisitor
from exactly_lib_test.type_val_deps.types.path.test_resources.path_relativity import equals_path_relativity_variants


def matches_value_restriction_failure(message: Assertion[TextRenderer]) -> Assertion[ErrorMessageWithFixTip]:
    return err_msg_w_fix_tip.matches(message)


def is__w_str_rendering() -> Assertion[ValueRestriction]:
    return matches__arbitrary_value(tuple(value_type.W_STR_RENDERING_TYPE_2_VALUE_TYPE.keys()))


def matches__arbitrary_value(accepted: Sequence[WithStrRenderingType]) -> Assertion[ValueRestriction]:
    return _IsValueRestrictionOfArbitraryValue(accepted)


def is__string() -> Assertion[ValueRestriction]:
    return matches__arbitrary_value((WithStrRenderingType.STRING,))


def equals__path_w_relativity(expected: PathAndRelativityRestriction) -> Assertion[ValueRestriction]:
    return asrt.is_instance_with(PathAndRelativityRestriction,
                                 asrt.sub_component('accepted',
                                                    PathAndRelativityRestriction.accepted.fget,
                                                    equals_path_relativity_variants(expected.accepted)))


def is__path_w_relativity() -> Assertion[ValueRestriction]:
    return asrt.is_instance(PathAndRelativityRestriction)


def equals(expected: ValueRestriction) -> Assertion[ValueRestriction]:
    return _EqualsValueRestriction(expected)


class _EqualsValueRestriction(AssertionBase[ValueRestriction]):
    def __init__(self, expected: ValueRestriction):
        self.expected = expected

    def _apply(self,
               put: unittest.TestCase,
               value,
               message_builder: asrt.MessageBuilder):
        _EqualsValueRestrictionVisitor(value, put, message_builder).visit(self.expected)


class _EqualsValueRestrictionVisitor(ProdValueRestrictionVariantsVisitor):
    def __init__(self,
                 actual,
                 put: unittest.TestCase,
                 message_builder: asrt.MessageBuilder):
        self.message_builder = message_builder
        self.actual = actual
        self.put = put

    def visit_any(self, expected: ArbitraryValueWStrRenderingRestriction):
        matches__arbitrary_value(expected.accepted).apply(self.put, self.actual, self.message_builder)

    def visit_path_relativity(self, expected: PathAndRelativityRestriction):
        equals__path_w_relativity(expected).apply(self.put, self.actual, self.message_builder)


class _IsValueRestrictionOfArbitraryValue(AssertionBase[ValueRestriction]):
    def __init__(self, accepted: Sequence[WithStrRenderingType]):
        self._accepted = accepted

    def _apply(self,
               put: unittest.TestCase,
               value: ValueRestriction,
               message_builder: MessageBuilder,
               ):
        put.assertIsInstance(value,
                             ArbitraryValueWStrRenderingRestriction,
                             message_builder.apply('object type'))
        assert isinstance(value, ArbitraryValueWStrRenderingRestriction)  # Type info for IDE
        put.assertEqual(self._accepted,
                        value.accepted,
                        message_builder.apply('accepted types'))
