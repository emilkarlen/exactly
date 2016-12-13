import unittest

from exactly_lib.common.help import see_also as struct
from exactly_lib_test.common.help.test_resources import cross_reference_id_va
from exactly_lib_test.test_resources.value_assertions import value_assertion as va
from exactly_lib_test.util.textformat.test_resources import structure as struct_check


class _IsSeeAlsoItemVa(va.ValueAssertion):
    _class_assertion = va.IsInstance(struct.SeeAlsoItem)

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: va.MessageBuilder = va.MessageBuilder()):
        self._class_assertion.apply(put, value, message_builder)
        _IsSeeAlsoItem(put, message_builder).visit(value)


class _IsSeeAlsoItem(struct.SeeAlsoItemVisitor):
    def __init__(self,
                 put: unittest.TestCase,
                 message_builder: va.MessageBuilder):
        self.put = put
        self.message_builder = message_builder

    def visit_text(self, x: struct.TextSeeAlsoItem):
        assertion = va.sub_component('text',
                                     struct.TextSeeAlsoItem.text.fget,
                                     struct_check.is_text)
        assertion.apply(self.put, x, self.message_builder)

    def visit_cross_reference_id(self, x: struct.CrossReferenceIdSeeAlsoItem):
        assertion = va.sub_component('cross_reference_id',
                                     struct.CrossReferenceIdSeeAlsoItem.cross_reference_id.fget,
                                     cross_reference_id_va.is_any)
        assertion.apply(self.put, x, self.message_builder)


is_see_also_item = _IsSeeAlsoItemVa()

is_see_also_item_list = va.is_list_of(is_see_also_item)
