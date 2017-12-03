import unittest

from exactly_lib.common.help import see_also as struct
from exactly_lib.common.help.see_also import SeeAlsoSet
from exactly_lib.help_texts.cross_ref.app_cross_ref import SeeAlsoTarget, CrossReferenceId
from exactly_lib_test.help_texts.test_resources import cross_reference_id_va
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.textformat.test_resources import structure as struct_check


class _IsSeeAlsoItemVa(asrt.ValueAssertion):
    _class_assertion = asrt.IsInstance(struct.SeeAlsoItem)

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        self._class_assertion.apply(put, value, message_builder)
        _IsSeeAlsoItem(put, message_builder).visit(value)


class _IsSeeAlsoItem(struct.SeeAlsoItemVisitor):
    def __init__(self,
                 put: unittest.TestCase,
                 message_builder: asrt.MessageBuilder):
        self.put = put
        self.message_builder = message_builder

    def visit_text(self, x: struct.TextSeeAlsoItem):
        assertion = asrt.sub_component('text',
                                       struct.TextSeeAlsoItem.text.fget,
                                       struct_check.is_text)
        assertion.apply(self.put, x, self.message_builder)

    def visit_cross_reference_id(self, x: struct.CrossReferenceIdSeeAlsoItem):
        assertion = asrt.sub_component('cross_reference_id',
                                       struct.CrossReferenceIdSeeAlsoItem.cross_reference_id.fget,
                                       cross_reference_id_va.is_any)
        assertion.apply(self.put, x, self.message_builder)


class _IsSeeAlsoTarget(asrt.ValueAssertion):
    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        if isinstance(value, CrossReferenceId):
            cross_reference_id_va.is_any.apply_with_message(put,
                                                            value,
                                                            str(CrossReferenceId))
        elif isinstance(value, struct.SeeAlsoUrlInfo):
            is_see_also_url_info.apply_with_message(put, value,
                                                    str(struct.SeeAlsoUrlInfo))
        else:
            put.fail('Not a {}: {}'.format(SeeAlsoTarget,
                                           value
                                           ))


is_see_also_url_info = asrt.is_instance_with(struct.SeeAlsoUrlInfo,
                                             asrt.and_([
                                                 asrt.sub_component('name',
                                                                    struct.SeeAlsoUrlInfo.title.fget,
                                                                    asrt.is_instance(str)),
                                                 asrt.sub_component('url',
                                                                    struct.SeeAlsoUrlInfo.url.fget,
                                                                    asrt.is_instance(str)),
                                             ]))
is_see_also_item = _IsSeeAlsoItemVa()

is_see_also_item_list = asrt.is_list_of(is_see_also_item)

is_see_also_target = _IsSeeAlsoTarget()

is_see_also_target_list = asrt.is_list_of(is_see_also_target)

is_see_also_set_with_valid_contents = asrt.is_instance_with(SeeAlsoSet,
                                                            asrt.sub_component('see_also_items',
                                                                               SeeAlsoSet.see_also_items.fget,
                                                                               is_see_also_item_list))
