from abc import ABC, abstractmethod
from typing import Sequence

from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.symbol.resolver_with_validation import ObjectWithSymbolReferencesAndValidation
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases import common as i
from exactly_lib.test_case.phases.common import InstructionSourceInfo
from exactly_lib.test_case.validation import pre_or_post_validation
from exactly_lib.test_case.validation.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case_utils.err_msg.path_description import path_value_description
from exactly_lib.test_case_utils.err_msg.property_description import file_property_name
from exactly_lib.test_case_utils.err_msg2.described_path import DescribedPathPrimitive
from exactly_lib.test_case_utils.err_msg2.path_impl import described_path_resolvers
from exactly_lib.type_system.error_message import PropertyDescriptor, FilePropertyDescriptorConstructor


class ComparisonActualFile(tuple):
    def __new__(cls,
                actual_path: DescribedPathPrimitive,
                checked_file_describer: FilePropertyDescriptorConstructor,
                file_access_needs_to_be_verified: bool
                ):
        return tuple.__new__(cls, (checked_file_describer,
                                   actual_path,
                                   file_access_needs_to_be_verified))

    @property
    def checked_file_describer(self) -> FilePropertyDescriptorConstructor:
        return self[0]

    @property
    def path(self) -> DescribedPathPrimitive:
        return self[1]

    @property
    def file_access_needs_to_be_verified(self) -> bool:
        return self[2]


class ComparisonActualFileConstructor(ObjectWithSymbolReferencesAndValidation, ABC):
    @abstractmethod
    def construct(self,
                  source_info: InstructionSourceInfo,
                  environment: i.InstructionEnvironmentForPostSdsStep,
                  os_services: OsServices) -> ComparisonActualFile:
        pass


class ConstructorForPath(ComparisonActualFileConstructor):
    def __init__(self,
                 path: FileRefResolver,
                 object_name: str,
                 file_access_needs_to_be_verified: bool,
                 ):
        """

        :param path: The path of the file that represents the actual string.
        :param object_name: Tells what "path" is representing.
        :param file_access_needs_to_be_verified: Tells if the path
        referred to by "path" may be invalid (e.g. do not exist), and
        thus need to be verified before it can be used, and the result of
        this verification may be that the path is invalid and thus the
        operation must be aborted with an explaining error message.
        """
        self._path = path
        self._object_name = object_name
        self._file_access_needs_to_be_verified = file_access_needs_to_be_verified

    def construct(self,
                  source_info: InstructionSourceInfo,
                  environment: i.InstructionEnvironmentForPostSdsStep,
                  os_services: OsServices) -> ComparisonActualFile:
        return ComparisonActualFile(
            described_path_resolvers.of(self._path)
                .resolve__with_cwd_as_cd(environment.symbols)
                .value_of_any_dependency(environment.home_and_sds),
            ActualFilePropertyDescriptorConstructorForComparisonFile(
                self._path,
                self._object_name),
            self._file_access_needs_to_be_verified,
        )

    @property
    def validator(self) -> PreOrPostSdsValidator:
        return pre_or_post_validation.ConstantSuccessValidator()

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._path.references


class ActualFilePropertyDescriptorConstructorForComparisonFile(FilePropertyDescriptorConstructor):
    def __init__(self,
                 file_ref: FileRefResolver,
                 object_name: str):
        self._file_ref = file_ref
        self._object_name = object_name

    def construct_for_contents_attribute(self, contents_attribute: str) -> PropertyDescriptor:
        return path_value_description(file_property_name(contents_attribute, self._object_name),
                                      self._file_ref)
