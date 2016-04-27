import unittest

from exactly_lib.help.cross_reference_id import TargetInfoNode, TargetInfo
from exactly_lib.util.textformat.structure import core
from shellcheck_lib_test.test_resources import value_assertion as va


class IsTargetInfoNode(va.ValueAssertion):
    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: va.MessageBuilder = va.MessageBuilder()):
        va.IsInstance(TargetInfoNode).apply(put, value, message_builder)
        va.sub_component('data',
                         TargetInfoNode.data.fget,
                         is_target_info).apply(put, value, message_builder)
        va.sub_component_list('children',
                              TargetInfoNode.children.fget,
                              self).apply(put, value, message_builder)


is_target_info_hierarchy = va.every_element('nodes', IsTargetInfoNode(), '')

is_target_info = va.And([
    va.IsInstance(TargetInfo),
    va.sub_component('presentation',
                     TargetInfo.presentation_str.fget,
                     va.IsInstance(str)),
    va.sub_component('target',
                     TargetInfo.target.fget,
                     va.IsInstance(core.CrossReferenceTarget)),
])
