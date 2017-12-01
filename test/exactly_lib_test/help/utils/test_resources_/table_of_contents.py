import unittest

from exactly_lib.help_texts.cross_reference_id import TargetInfoNode, TargetInfo, CrossReferenceId
from exactly_lib.util.textformat.structure import core
from exactly_lib_test.help_texts.test_resources import cross_reference_id_va as cross_ref_va
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.textformat.test_resources.structure import is_string_text

is_target_info = asrt.And([
    asrt.IsInstance(TargetInfo),
    asrt.sub_component('presentation',
                       TargetInfo.presentation_text.fget,
                       is_string_text),
    asrt.sub_component('target',
                       TargetInfo.target.fget,
                       asrt.IsInstance(core.CrossReferenceTarget)),
])


def equals_target_info(expected: TargetInfo) -> asrt.ValueAssertion:
    return _IsTargetInfoAndEquals(expected)


class _IsTargetInfoAndEquals(asrt.ValueAssertion):
    _can_only_check_CrossReferenceId = 'Can only check equality of target of type ' + str(CrossReferenceId)

    def __init__(self, expected: TargetInfo):
        self.expected = expected
        assert isinstance(self.expected.target, CrossReferenceId), self._can_only_check_CrossReferenceId

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        is_target_info.apply(put, value, message_builder)
        assert isinstance(value, TargetInfo)
        put.assertEqual(self.expected.presentation_text.value,
                        value.presentation_text.value,
                        message_builder.apply('presentation_str'))
        put.assertIsInstance(value.target, CrossReferenceId,
                             'Actual value is not a ' + str(CrossReferenceId))
        expected_target = self.expected.target
        assert isinstance(expected_target, CrossReferenceId)
        cross_ref_va.equals(expected_target).apply(put, value.target,
                                                   message_builder.for_sub_component('target'))


class _IsTargetInfoNode(asrt.ValueAssertion):
    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        _is_TargetInfoNodeObject_shallow.apply(put, value, message_builder)
        asrt.sub_component_list('children',
                                TargetInfoNode.children.fget,
                                self).apply(put, value, message_builder)


_is_TargetInfoNodeObject_shallow = asrt.And([
    asrt.IsInstance(TargetInfoNode),
    asrt.sub_component('data',
                       TargetInfoNode.data.fget,
                       is_target_info),
    asrt.sub_component('children',
                       TargetInfoNode.children.fget,
                       asrt.IsInstance(list)),
])

is_target_info_node = _IsTargetInfoNode()

is_target_info_node_list = asrt.every_element('nodes', is_target_info_node, '')


def _equals_target_info_node__shallow(expected: TargetInfoNode) -> asrt.ValueAssertion:
    return asrt.And([
        _is_TargetInfoNodeObject_shallow,
        asrt.sub_component('target_info',
                           TargetInfoNode.data.fget,
                           equals_target_info(expected.data)),
        asrt.sub_component('children',
                           TargetInfoNode.children.fget,
                           asrt.len_equals(len(expected.children), 'Number of children'))
    ])


class _TargetInfoNodeEqual(asrt.ValueAssertion):
    def __init__(self, expected: TargetInfoNode):
        self.expected = expected

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        _equals_target_info_node__shallow(self.expected).apply(put, value, message_builder)
        assert isinstance(value, TargetInfoNode)
        for idx, child in enumerate(self.expected.children):
            equals_target_info_node(child).apply(put,
                                                 value.children[idx],
                                                 message_builder.for_sub_component('children[%d]' % idx))


def equals_target_info_node(expected: TargetInfoNode) -> asrt.ValueAssertion:
    """
    Traverses every node in the node tree, and checks that it is equal to the corresponding
    node in the expected node tree.
    """
    return _TargetInfoNodeEqual(expected)
