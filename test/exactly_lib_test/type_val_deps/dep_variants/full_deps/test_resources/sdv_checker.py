import unittest
from typing import Generic, Type, TypeVar

from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.type_val_deps.dep_variants.ddv.full_deps.ddv import FullDepsWithNodeDescriptionDdv, FullDepsDdv
from exactly_lib.type_val_deps.dep_variants.sdv.full_deps.sdv import FullDepsSdv
from exactly_lib.type_val_prims.description.details_structured import WithDetailsDescription
from exactly_lib.type_val_prims.description.tree_structured import WithNodeDescription
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder, Assertion
from exactly_lib_test.type_val_deps.dep_variants.full_deps.test_resources.common_properties_checker import \
    CommonSdvPropertiesChecker, PRIMITIVE, OUTPUT, CommonExecutionPropertiesChecker
from exactly_lib_test.type_val_deps.dep_variants.test_resources.logic_structure_assertions import has_valid_description
from exactly_lib_test.type_val_deps.test_resources.full_deps import full_sdv_assertions as asrt_logic
from exactly_lib_test.util.description_tree.test_resources import described_tree_assertions as asrt_d_tree, \
    rendering_assertions as asrt_trace_rendering


class FullDepsSdvPropertiesChecker(Generic[PRIMITIVE],
                                   CommonSdvPropertiesChecker[PRIMITIVE]):
    def __init__(self, expected_object_type: Type[FullDepsSdv]):
        self._is_valid_sdv = asrt_logic.matches_sdv_attributes(
            expected_object_type,
            asrt.is_sequence_of(asrt.is_instance(SymbolReference))
        )

    def check(self,
              put: unittest.TestCase,
              actual: FullDepsSdv[PRIMITIVE],
              message_builder: MessageBuilder,
              ):
        asrt.is_instance(FullDepsSdv).apply(put,
                                            actual,
                                            message_builder.for_sub_component('type'))
        assert isinstance(actual, FullDepsSdv)  # Type info for IDE
        self._is_valid_sdv.apply(put, actual, message_builder)


PRIM_W_NODE_DESC = TypeVar('PRIM_W_NODE_DESC', bound=WithNodeDescription)


class WithNodeDescriptionExecutionPropertiesChecker(
    Generic[PRIM_W_NODE_DESC, OUTPUT],
    CommonExecutionPropertiesChecker[PRIM_W_NODE_DESC, OUTPUT]
):

    def __init__(self,
                 expected_ddv_object_type: Type[FullDepsWithNodeDescriptionDdv],
                 expected_primitive_object_type: Type[PRIM_W_NODE_DESC],
                 application_output: Assertion[OUTPUT],
                 ):
        self._expected_ddv_object_type = expected_ddv_object_type
        self._expected_primitive_object_type = expected_primitive_object_type
        self._application_output = application_output
        self._structure_tree_of_ddv = None

    def check_ddv(self,
                  put: unittest.TestCase,
                  actual: FullDepsDdv[PRIM_W_NODE_DESC],
                  message_builder: MessageBuilder,
                  ):
        asrt.is_instance(self._expected_ddv_object_type).apply(
            put,
            actual,
            message_builder.for_sub_component('object type'),
        )

        assert isinstance(actual, WithNodeDescription)  # Type info for IDE

        self._structure_tree_of_ddv = actual.structure().render()

        asrt_d_tree.matches_node().apply(
            put,
            self._structure_tree_of_ddv,
            message_builder.for_sub_component('sanity of structure'),
        )

        has_valid_description().apply(put, actual, message_builder)

    def check_primitive(self,
                        put: unittest.TestCase,
                        actual: PRIM_W_NODE_DESC,
                        message_builder: MessageBuilder,
                        ):
        asrt.is_instance(self._expected_primitive_object_type).apply(
            put,
            actual,
            message_builder.for_sub_component('object type'),
        )

        self._check_structure_of_primitive(put, actual, message_builder)

    def check_application_output(self,
                                 put: unittest.TestCase,
                                 actual: OUTPUT,
                                 message_builder: MessageBuilder):
        self._application_output.apply(put, actual, message_builder)

    def _check_structure_of_primitive(self,
                                      put: unittest.TestCase,
                                      actual: PRIM_W_NODE_DESC,
                                      message_builder: MessageBuilder,
                                      ):
        structure_tree_of_primitive = actual.structure().render()

        asrt_d_tree.matches_node().apply(
            put,
            structure_tree_of_primitive,
            message_builder.for_sub_component('sanity of structure'),
        )

        structure_equals_ddv = asrt_d_tree.header_data_and_children_equal_as(self._structure_tree_of_ddv)

        structure_equals_ddv.apply_with_message(
            put,
            structure_tree_of_primitive,
            'structure of should be same as that of ddv',
        )


PRIM_W_DETAIL_DESC = TypeVar('PRIM_W_DETAIL_DESC', bound=WithDetailsDescription)


class WithDetailsDescriptionExecutionPropertiesChecker(
    Generic[PRIM_W_DETAIL_DESC, OUTPUT],
    CommonExecutionPropertiesChecker[PRIM_W_DETAIL_DESC, OUTPUT]
):
    def __init__(self,
                 expected_ddv_object_type: Type[WithDetailsDescription],
                 expected_primitive_object_type: Type[PRIM_W_DETAIL_DESC],
                 application_output: Assertion[OUTPUT],
                 ):
        self._expected_ddv_object_type = expected_ddv_object_type
        self._expected_primitive_object_type = expected_primitive_object_type
        self._application_output = application_output

    def check_ddv(self,
                  put: unittest.TestCase,
                  actual: FullDepsDdv[PRIM_W_DETAIL_DESC],
                  message_builder: MessageBuilder,
                  ):
        asrt.is_instance(self._expected_ddv_object_type).apply(
            put,
            actual,
            message_builder.for_sub_component('object type'),
        )

        assert isinstance(actual, WithDetailsDescription)  # Type info for IDE

        self._check_sanity_of_details_renderer(put, message_builder, actual)

        has_valid_description().apply(put, actual, message_builder)

    def check_primitive(self,
                        put: unittest.TestCase,
                        actual: PRIM_W_DETAIL_DESC,
                        message_builder: MessageBuilder,
                        ):
        asrt.is_instance(self._expected_primitive_object_type).apply(
            put,
            actual,
            message_builder.for_sub_component('object type'),
        )

        self._check_sanity_of_details_renderer(put, message_builder, actual)

    def check_application_output(self,
                                 put: unittest.TestCase,
                                 actual: OUTPUT,
                                 message_builder: MessageBuilder):
        self._application_output.apply(put, actual, message_builder)

    @staticmethod
    def _check_sanity_of_details_renderer(put: unittest.TestCase,
                                          message_builder: MessageBuilder,
                                          actual: PRIM_W_DETAIL_DESC,
                                          ):
        expectation = asrt_trace_rendering.matches_details_renderer()
        expectation.apply(put, actual.describer, message_builder.for_sub_component('details description'))
