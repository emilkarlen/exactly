import pathlib
from typing import Sequence, Optional

from exactly_lib.definitions.actual_file_attributes import PLAIN_FILE_OBJECT_NAME, OUTPUT_FROM_PROGRAM_OBJECT_NAME
from exactly_lib.symbol.data import file_ref_resolvers
from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.symbol.resolver_with_validation import ObjectWithSymbolReferencesAndValidation
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case import pre_or_post_validation
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases import common as i
from exactly_lib.test_case.phases.common import InstructionSourceInfo
from exactly_lib.test_case.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case_utils.err_msg.path_description import path_value_description
from exactly_lib.test_case_utils.err_msg.property_description import file_property_name
from exactly_lib.test_case_utils.file_properties import must_exist_as, FileType
from exactly_lib.test_case_utils.file_ref_check import pre_or_post_sds_failure_message_or_none, FileRefCheck
from exactly_lib.type_system.data import file_refs
from exactly_lib.type_system.error_message import PropertyDescriptor, FilePropertyDescriptorConstructor


class ComparisonActualFileResolver:
    @property
    def property_descriptor_constructor(self) -> FilePropertyDescriptorConstructor:
        return _ActualFilePropertyDescriptorConstructorForComparisonFile(self.file_ref_resolver(),
                                                                         self.object_name())

    def object_name(self) -> str:
        raise NotImplementedError('abstract method')

    def file_check_failure(self, environment: i.InstructionEnvironmentForPostSdsStep) -> Optional[str]:
        """
        :return: None iff there is no failure.
        """
        raise NotImplementedError()

    def file_ref_resolver(self) -> FileRefResolver:
        raise NotImplementedError('abstract method')


class ComparisonActualFileConstructor(ObjectWithSymbolReferencesAndValidation):
    def construct(self,
                  source_info: InstructionSourceInfo,
                  environment: i.InstructionEnvironmentForPostSdsStep,
                  os_services: OsServices) -> ComparisonActualFileResolver:
        raise NotImplementedError('abstract method')


class ComparisonActualFileResolverConstantWithReferences(ComparisonActualFileResolver):
    def __init__(self, references: Sequence[SymbolReference]):
        self._references = references

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references


class ComparisonActualFileConstructorForConstant(ComparisonActualFileConstructor):
    def __init__(self, constructed_value: ComparisonActualFileResolverConstantWithReferences):
        self._constructed_value = constructed_value

    def construct(self,
                  source_info: InstructionSourceInfo,
                  environment: i.InstructionEnvironmentForPostSdsStep,
                  os_services: OsServices) -> ComparisonActualFileResolver:
        return self._constructed_value

    @property
    def validator(self) -> PreOrPostSdsValidator:
        return pre_or_post_validation.ConstantSuccessValidator()

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._constructed_value.references


class _ActualFilePropertyDescriptorConstructorForComparisonFile(FilePropertyDescriptorConstructor):
    def __init__(self,
                 file_ref: FileRefResolver,
                 object_name: str):
        self._file_ref = file_ref
        self._object_name = object_name

    def construct_for_contents_attribute(self, contents_attribute: str) -> PropertyDescriptor:
        return path_value_description(file_property_name(contents_attribute, self._object_name),
                                      self._file_ref)


class ActComparisonActualFileForFileRef(ComparisonActualFileResolverConstantWithReferences):
    def __init__(self, file_ref_resolver: FileRefResolver):
        super().__init__(file_ref_resolver.references)
        self._file_ref_resolver = file_ref_resolver

    def object_name(self) -> str:
        return PLAIN_FILE_OBJECT_NAME

    def file_ref_resolver(self) -> FileRefResolver:
        return self._file_ref_resolver

    def file_check_failure(self, environment: i.InstructionEnvironmentForPostSdsStep) -> Optional[str]:
        return pre_or_post_sds_failure_message_or_none(FileRefCheck(self._file_ref_resolver,
                                                                    must_exist_as(FileType.REGULAR)),
                                                       environment.path_resolving_environment_pre_or_post_sds)


class ComparisonActualFileResolverForProgramOutput(ComparisonActualFileResolver):
    def __init__(self, file_with_program_output: pathlib.Path):
        self._file_with_program_output = file_with_program_output
        if not file_with_program_output.is_absolute():
            raise ValueError('Path must be absolute: ' + str(file_with_program_output))

    @property
    def property_descriptor_constructor(self) -> FilePropertyDescriptorConstructor:
        return _ActualFilePropertyDescriptorConstructorForComparisonFile(self.file_ref_resolver(),
                                                                         self.object_name())

    def object_name(self) -> str:
        return OUTPUT_FROM_PROGRAM_OBJECT_NAME

    def file_check_failure(self, environment: i.InstructionEnvironmentForPostSdsStep) -> Optional[str]:
        return None

    def file_ref_resolver(self) -> FileRefResolver:
        return file_ref_resolvers.constant(file_refs.absolute_path(self._file_with_program_output))
