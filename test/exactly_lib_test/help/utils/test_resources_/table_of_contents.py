import unittest

from exactly_lib.util.textformat.construction.section_hierarchy import TargetInfo, TargetInfoNode
from exactly_lib.util.textformat.structure import core
from exactly_lib.util.textformat.structure.core import CrossReferenceTarget
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


def equals_target_info(expected: TargetInfo,
                       mk_equals_cross_ref_id=lambda x: asrt.anything_goes()
                       ) -> asrt.ValueAssertion:
    return _IsTargetInfoAndEquals(expected, mk_equals_cross_ref_id)


def equals_target_info_node(expected: TargetInfoNode,
                            mk_equals_cross_ref_id=lambda x: asrt.anything_goes()
                            ) -> asrt.ValueAssertion:
    """
    Traverses every node in the node tree, and checks that it is equal to the corresponding
    node in the expected node tree.
    """
    return _TargetInfoNodeEqual(expected, mk_equals_cross_ref_id)


class _IsTargetInfoAndEquals(asrt.ValueAssertion):
    def __init__(self,
                 expected: TargetInfo,
                 mk_equals_cross_ref_id
                 ):
        self.expected = expected
        self.mk_equals_cross_ref_id = mk_equals_cross_ref_id

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        is_target_info.apply(put, value, message_builder)
        assert isinstance(value, TargetInfo)
        put.assertEqual(self.expected.presentation_text.value,
                        value.presentation_text.value,
                        message_builder.apply('presentation_str'))
        put.assertIsInstance(value.target, CrossReferenceTarget,
                             'Actual value is not a ' + str(CrossReferenceTarget))
        expected_target = self.expected.target
        assert isinstance(expected_target, CrossReferenceTarget)
        assertion = self.mk_equals_cross_ref_id(expected_target)
        assertion.apply(put,
                        value.target,
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


def _equals_target_info_node__shallow(expected: TargetInfoNode,
                                      mk_equals_cross_ref_id) -> asrt.ValueAssertion:
    return asrt.And([
        _is_TargetInfoNodeObject_shallow,
        asrt.sub_component('target_info',
                           TargetInfoNode.data.fget,
                           equals_target_info(expected.data,
                                              mk_equals_cross_ref_id)),
        asrt.sub_component('children',
                           TargetInfoNode.children.fget,
                           asrt.len_equals(len(expected.children), 'Number of children'))
    ])


class _TargetInfoNodeEqual(asrt.ValueAssertion):
    def __init__(self,
                 expected: TargetInfoNode,
                 mk_equals_cross_ref_id,
                 ):
        self.expected = expected
        self.mk_equals_cross_ref_id = mk_equals_cross_ref_id

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        assertion_on_shallow = _equals_target_info_node__shallow(self.expected,
                                                                 self.mk_equals_cross_ref_id)
        assertion_on_shallow.apply(put, value, message_builder)
        assert isinstance(value, TargetInfoNode)
        for idx, child in enumerate(self.expected.children):
            assertion = equals_target_info_node(child, self.mk_equals_cross_ref_id)
            assertion.apply(put,
                            value.children[idx],
                            message_builder.for_sub_component('children[%d]' % idx))
