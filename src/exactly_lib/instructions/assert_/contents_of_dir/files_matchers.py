from abc import ABC, abstractmethod
from typing import Optional

from exactly_lib.instructions.assert_.contents_of_dir.files_matcher import FilesMatcherResolver, FilesSource, \
    Environment
from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.symbol.resolver_structure import FileMatcherResolver
from exactly_lib.test_case import pre_or_post_validation
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case_utils.err_msg import property_description
from exactly_lib.test_case_utils.err_msg.path_description import PathValuePartConstructor
from exactly_lib.test_case_utils.file_matcher import parse_file_matcher
from exactly_lib.type_system.error_message import PropertyDescriptor, ErrorMessageResolver
from exactly_lib.util.logic_types import ExpectationType


class Settings:
    def __init__(self,
                 expectation_type: ExpectationType,
                 file_matcher: FileMatcherResolver):
        self.expectation_type = expectation_type
        self.file_matcher = file_matcher

    def property_descriptor(self,
                            property_name: str,
                            path_to_check: FileRefResolver) -> PropertyDescriptor:
        return property_descriptor(path_to_check, self.file_matcher, property_name)


def property_descriptor(path_to_check: FileRefResolver,
                        file_matcher: FileMatcherResolver,
                        property_name: str) -> PropertyDescriptor:
    return property_description.PropertyDescriptorWithConstantPropertyName(
        property_name,
        property_description.multiple_object_descriptors([
            PathValuePartConstructor(path_to_check),
            parse_file_matcher.FileSelectionDescriptor(file_matcher),
        ])
    )


class FilesMatcherResolverBase(FilesMatcherResolver, ABC):
    def __init__(self,
                 settings: Settings,
                 validator: PreOrPostSdsValidator = pre_or_post_validation.ConstantSuccessValidator()):
        self._settings = settings
        self._validator = validator

    def validator(self) -> PreOrPostSdsValidator:
        return self._validator

    @abstractmethod
    def matches(self,
                environment: Environment,
                os_services: OsServices,
                files_source: FilesSource) -> Optional[ErrorMessageResolver]:
        pass
