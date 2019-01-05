import pathlib
from typing import Optional

from exactly_lib.definitions import actual_file_attributes
from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils.err_msg import path_description, diff_msg_utils, diff_msg
from exactly_lib.type_system.error_message import ErrorMessageResolver, ErrorMessageResolvingEnvironment


class FileSystemElementReference:
    def __init__(self,
                 path_resolver: FileRefResolver,
                 resolved_path: pathlib.Path):
        self.path_resolver = path_resolver
        self.resolved_path = resolved_path


class FileSystemElementPropertiesMatcher:
    def __init__(self, properties_check: file_properties.ActualFilePropertiesResolver):
        self._properties_check = properties_check

    def matches(self, element: FileSystemElementReference) -> Optional[ErrorMessageResolver]:
        failure_info_properties = self._properties_check.resolve_failure_info(element.resolved_path)

        if failure_info_properties:
            return _ErrorMessageResolverForFailingFileProperties(element.path_resolver,
                                                                 failure_info_properties)
        else:
            return None


class _ErrorMessageResolverForFailingFileProperties(ErrorMessageResolver):
    def __init__(self,
                 failing_file: FileRefResolver,
                 failure: file_properties.Properties):
        self.failing_file = failing_file
        self.failure = failure

    def resolve(self, environment: ErrorMessageResolvingEnvironment) -> str:
        from exactly_lib.util.logic_types import ExpectationType

        property_descriptor = path_description.path_value_description(
            actual_file_attributes.PLAIN_FILE_OBJECT_NAME,
            self.failing_file)
        diff_failure_resolver = diff_msg_utils.DiffFailureInfoResolver(
            property_descriptor,
            ExpectationType.POSITIVE,
            diff_msg_utils.ConstantExpectedValueResolver('existing regular file'),
        )
        actual_info = diff_msg.ActualInfo(file_properties.render_property(self.failure))
        return diff_failure_resolver.resolve(environment, actual_info).error_message()
