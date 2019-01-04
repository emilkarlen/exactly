from abc import ABC, abstractmethod
from typing import Optional

from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.symbol.object_with_typed_symbol_references import ObjectWithTypedSymbolReferences
from exactly_lib.symbol.resolver_structure import FileMatcherResolver
from exactly_lib.test_case import pre_or_post_validation
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
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


class FilesSource:
    def __init__(self,
                 path_of_dir: FileRefResolver):
        self._path_of_dir = path_of_dir

    @property
    def path_of_dir(self) -> FileRefResolver:
        return self._path_of_dir


class FilesMatcherResolver(ObjectWithTypedSymbolReferences, ABC):
    @abstractmethod
    def validator(self) -> PreOrPostSdsValidator:
        pass

    @abstractmethod
    def matches(self,
                environment: InstructionEnvironmentForPostSdsStep,
                os_services: OsServices,
                files_source: FilesSource) -> Optional[ErrorMessageResolver]:
        pass


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
                environment: InstructionEnvironmentForPostSdsStep,
                os_services: OsServices,
                files_source: FilesSource) -> Optional[ErrorMessageResolver]:
        pass
