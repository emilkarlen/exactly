from typing import Optional

from exactly_lib.definitions import actual_file_attributes
from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils.err_msg import diff_msg_utils, diff_msg
from exactly_lib.type_system.data import path_description
from exactly_lib.type_system.data.described_path import DescribedPathPrimitive
from exactly_lib.type_system.data.path_describer import PathDescriberForPrimitive
from exactly_lib.type_system.err_msg.prop_descr import PropertyDescriptor
from exactly_lib.type_system.error_message import ErrorMessageResolver


class FileSystemElementPropertiesMatcher:
    def __init__(self, properties_check: file_properties.ActualFilePropertiesResolver):
        self._properties_check = properties_check

    def matches(self, element: DescribedPathPrimitive) -> Optional[ErrorMessageResolver]:
        failure_info_properties = self._properties_check.resolve_failure_info(element.primitive)

        if failure_info_properties:
            return _ErrorMessageResolverForFailingFileProperties(element.describer,
                                                                 failure_info_properties)
        else:
            return None


class _ErrorMessageResolverForFailingFileProperties(ErrorMessageResolver):
    def __init__(self,
                 failing_file: PathDescriberForPrimitive,
                 failure: file_properties.Properties):
        self.failing_file = failing_file
        self.failure = failure

    def resolve(self) -> str:
        from exactly_lib.util.logic_types import ExpectationType

        property_descriptor = path_description.path_value_description(
            actual_file_attributes.PLAIN_FILE_OBJECT_NAME,
            self.failing_file,
            True,
        )
        diff_failure_resolver = diff_msg_utils.DiffFailureInfoResolver(
            property_descriptor,
            ExpectationType.POSITIVE,
            diff_msg_utils.ConstantExpectedValueResolver('existing regular file'),
        )
        actual_info = diff_msg.ActualInfo(file_properties.render_property(self.failure))
        return diff_failure_resolver.resolve(actual_info).error_message()


class ErrorMessageResolverForFailingFileProperties2(ErrorMessageResolver):
    def __init__(self,
                 failing_file_property_descriptor: PropertyDescriptor,
                 failure: file_properties.Properties,
                 expected: file_properties.FileType):
        self.expected = expected
        self.failing_file_property_descriptor = failing_file_property_descriptor
        self.failure = failure

    def resolve(self) -> str:
        from exactly_lib.util.logic_types import ExpectationType

        expected_file_type_description = file_properties.TYPE_INFO[self.expected].description

        diff_failure_resolver = diff_msg_utils.DiffFailureInfoResolver(
            self.failing_file_property_descriptor,
            ExpectationType.POSITIVE,
            diff_msg_utils.ConstantExpectedValueResolver('existing ' + expected_file_type_description),
        )
        actual_info = diff_msg.ActualInfo(file_properties.render_property(self.failure))
        return diff_failure_resolver.resolve(actual_info).error_message()
