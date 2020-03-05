import unittest
from typing import Generic, Type

from exactly_lib.symbol.logic.logic_type_sdv import LogicSdv
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.type_system.description.details_structured import WithDetailsDescription
from exactly_lib.type_system.description.tree_structured import WithTreeStructureDescription
from exactly_lib.type_system.logic.logic_base_class import LogicWithStructureDdv, LogicDdv
from exactly_lib_test.test_case_utils.logic.test_resources import assertions as asrt_logic
from exactly_lib_test.test_case_utils.logic.test_resources.common_properties_checker import \
    CommonSdvPropertiesChecker, PRIMITIVE, CommonExecutionPropertiesChecker
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder
from exactly_lib_test.type_system.logic.test_resources.logic_structure_assertions import has_valid_description
from exactly_lib_test.util.description_tree.test_resources import described_tree_assertions as asrt_d_tree


class LogicSdvPropertiesChecker(Generic[PRIMITIVE],
                                CommonSdvPropertiesChecker[PRIMITIVE]):
    def __init__(self, expected_object_type: Type[LogicSdv]):
        self._is_valid_sdv = asrt_logic.matches_logic_sdv_attributes(
            expected_object_type,
            asrt.is_sequence_of(asrt.is_instance(SymbolReference))
        )

    def check(self,
              put: unittest.TestCase,
              actual: LogicSdv[PRIMITIVE],
              message_builder: MessageBuilder,
              ):
        asrt.is_instance(LogicSdv).apply(put,
                                         actual,
                                         message_builder.for_sub_component('type'))
        assert isinstance(actual, LogicSdv)  # Type info for IDE
        self._is_valid_sdv.apply(put, actual, message_builder)


class WithTreeStructureExecutionPropertiesChecker(CommonExecutionPropertiesChecker[WithTreeStructureDescription]):
    def __init__(self,
                 expected_ddv_object_type: Type[LogicWithStructureDdv],
                 expected_primitive_object_type: Type[WithTreeStructureDescription],
                 ):
        self._expected_ddv_object_type = expected_ddv_object_type
        self._expected_primitive_object_type = expected_primitive_object_type
        self._structure_tree_of_ddv = None

    def check_ddv(self,
                  put: unittest.TestCase,
                  actual: LogicDdv[WithTreeStructureDescription],
                  message_builder: MessageBuilder,
                  ):
        asrt.is_instance(self._expected_ddv_object_type).apply(
            put,
            actual,
            message_builder.for_sub_component('object type'),
        )

        assert isinstance(actual, WithTreeStructureDescription)  # Type info for IDE

        self._structure_tree_of_ddv = actual.structure().render()

        asrt_d_tree.matches_node().apply(
            put,
            self._structure_tree_of_ddv,
            message_builder.for_sub_component('sanity of structure'),
        )

        has_valid_description().apply(put, actual, message_builder)

    def check_primitive(self,
                        put: unittest.TestCase,
                        actual: WithTreeStructureDescription,
                        message_builder: MessageBuilder,
                        ):
        asrt.is_instance(self._expected_primitive_object_type).apply(
            put,
            actual,
            message_builder.for_sub_component('object type'),
        )

        self._check_structure_of_primitive(put, actual, message_builder)

    def _check_structure_of_primitive(self,
                                      put: unittest.TestCase,
                                      actual: WithTreeStructureDescription,
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


class WithDetailsDescriptionExecutionPropertiesChecker(CommonExecutionPropertiesChecker[WithDetailsDescription]):
    def __init__(self,
                 expected_ddv_object_type: Type[WithDetailsDescription],
                 expected_primitive_object_type: Type[WithDetailsDescription],
                 ):
        self._expected_ddv_object_type = expected_ddv_object_type
        self._expected_primitive_object_type = expected_primitive_object_type

    def check_ddv(self,
                  put: unittest.TestCase,
                  actual: LogicDdv[WithDetailsDescription],
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
                        actual: WithDetailsDescription,
                        message_builder: MessageBuilder,
                        ):
        asrt.is_instance(self._expected_primitive_object_type).apply(
            put,
            actual,
            message_builder.for_sub_component('object type'),
        )

        self._check_sanity_of_details_renderer(put, message_builder, actual)

    @staticmethod
    def _check_sanity_of_details_renderer(put: unittest.TestCase,
                                          message_builder: MessageBuilder,
                                          actual: WithDetailsDescription,
                                          ):
        details = actual.describer.render()

        assertion = asrt.is_sequence_of(asrt_d_tree.is_any_detail())

        assertion.apply(
            put,
            details,
            message_builder.for_sub_component('sanity of description'),
        )
