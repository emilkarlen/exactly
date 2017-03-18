import unittest

from exactly_lib.common.help.cross_reference_id import TargetInfoNode, TargetInfo, CrossReferenceId
from exactly_lib.util.textformat.structure import core
from exactly_lib_test.common.help.test_resources import cross_reference_id_va as cross_ref_va
from exactly_lib_test.test_resources.value_assertions import value_assertion as va

is_target_info = va.And([
    va.IsInstance(TargetInfo),
    va.sub_component('presentation',
                     TargetInfo.presentation_str.fget,
                     va.IsInstance(str)),
    va.sub_component('target',
                     TargetInfo.target.fget,
                     va.IsInstance(core.CrossReferenceTarget)),
])


def equals_target_info(expected: TargetInfo) -> va.ValueAssertion:
    return _IsTargetInfoAndEquals(expected)


class _IsTargetInfoAndEquals(va.ValueAssertion):
    _can_only_check_CrossReferenceId = 'Can only check equality of target of type ' + str(CrossReferenceId)

    def __init__(self, expected: TargetInfo):
        self.expected = expected
        assert isinstance(self.expected.target, CrossReferenceId), self._can_only_check_CrossReferenceId

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: va.MessageBuilder = va.MessageBuilder()):
        is_target_info.apply(put, value, message_builder)
        assert isinstance(value, TargetInfo)
        put.assertEqual(self.expected.presentation_str,
                        value.presentation_str,
                        message_builder.apply('presentation_str'))
        put.assertIsInstance(value.target, CrossReferenceId,
                             'Actual value is not a ' + str(CrossReferenceId))
        expected_target = self.expected.target
        assert isinstance(expected_target, CrossReferenceId)
        cross_ref_va.equals(expected_target).apply(put, value.target,
                                                   message_builder.for_sub_component('target'))


class _IsTargetInfoNode(va.ValueAssertion):
    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: va.MessageBuilder = va.MessageBuilder()):
        _is_TargetInfoNodeObject_shallow.apply(put, value, message_builder)
        va.sub_component_list('children',
                              TargetInfoNode.children.fget,
                              self).apply(put, value, message_builder)


_is_TargetInfoNodeObject_shallow = va.And([
    va.IsInstance(TargetInfoNode),
    va.sub_component('data',
                     TargetInfoNode.data.fget,
                     is_target_info),
    va.sub_component('children',
                     TargetInfoNode.children.fget,
                     va.IsInstance(list)),
])

is_target_info_node = _IsTargetInfoNode()

is_target_info_node_list = va.every_element('nodes', is_target_info_node, '')


def _equals_target_info_node__shallow(expected: TargetInfoNode) -> va.ValueAssertion:
    return va.And([
        _is_TargetInfoNodeObject_shallow,
        va.sub_component('target_info',
                         TargetInfoNode.data.fget,
                         equals_target_info(expected.data)),
        va.sub_component('children',
                         TargetInfoNode.children.fget,
                         va.len_equals(len(expected.children), 'Number of children'))
    ])


class _TargetInfoNodeEqual(va.ValueAssertion):
    def __init__(self, expected: TargetInfoNode):
        self.expected = expected

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: va.MessageBuilder = va.MessageBuilder()):
        _equals_target_info_node__shallow(self.expected).apply(put, value, message_builder)
        assert isinstance(value, TargetInfoNode)
        for idx, child in enumerate(self.expected.children):
            equals_target_info_node(child).apply(put,
                                                 value.children[idx],
                                                 message_builder.for_sub_component('children[%d]' % idx))


def equals_target_info_node(expected: TargetInfoNode) -> va.ValueAssertion:
    """
    Traverses every node in the node tree, and checks that it is equal to the corresponding
    node in the expected node tree.
    """
    return _TargetInfoNodeEqual(expected)
