import pathlib
from typing import Sequence

from exactly_lib.instructions.assert_.utils.assertion_part import AssertionPart
from exactly_lib.instructions.assert_.utils.file_contents.actual_files import ComparisonActualFileResolver, \
    ComparisonActualFileConstructor
from exactly_lib.instructions.utils.error_messages import err_msg_env_from_instr_env
from exactly_lib.symbol.data import file_ref_resolvers
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, InstructionSourceInfo
from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils.file_system_element_matcher import \
    FileSystemElementReference, FileSystemElementPropertiesMatcher
from exactly_lib.test_case_utils.return_pfh_via_exceptions import PfhFailException, PfhHardErrorException
from exactly_lib.type_system.data.file_ref import FileRef
from exactly_lib.type_system.error_message import FilePropertyDescriptorConstructor
from exactly_lib.type_system.logic.string_matcher import DestinationFilePathGetter, FileToCheck
from exactly_lib.type_system.logic.string_transformer import IdentityStringTransformer


class ComparisonActualFile(tuple):
    def __new__(cls,
                actual_file_path: pathlib.Path,
                actual_file: FileRef,
                checked_file_describer: FilePropertyDescriptorConstructor,
                ):
        return tuple.__new__(cls, (actual_file_path, checked_file_describer, actual_file))

    @property
    def actual_file_path(self) -> pathlib.Path:
        return self[0]

    @property
    def checked_file_describer(self) -> FilePropertyDescriptorConstructor:
        return self[1]

    @property
    def actual_file(self) -> FileRef:
        return self[2]


class FileConstructorAssertionPart(AssertionPart[ComparisonActualFileConstructor, ComparisonActualFileResolver]):
    """
    Constructs the actual file.
    """

    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              custom_environment: InstructionSourceInfo,
              value_to_check: ComparisonActualFileConstructor) -> ComparisonActualFileResolver:
        return value_to_check.construct(custom_environment,
                                        environment,
                                        os_services)


class ConstructFileToCheckAssertionPart(AssertionPart[ComparisonActualFile, FileToCheck]):
    @property
    def references(self) -> Sequence[SymbolReference]:
        return ()

    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              custom_environment,
              file_to_transform: ComparisonActualFile,
              ) -> FileToCheck:
        actual_file_path = file_to_transform.actual_file_path

        return FileToCheck(actual_file_path,
                           file_to_transform.checked_file_describer,
                           environment.phase_logging.space_for_instruction(),
                           IdentityStringTransformer(),
                           DestinationFilePathGetter())


class FileExistenceAssertionPart(AssertionPart[ComparisonActualFileResolver, ComparisonActualFile]):
    """
    Checks existence of a :class:`ComparisonActualFile`,

    and returns it's path, if it exists.

    :raises PfhFailException: File does not exist.
    """

    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              custom_environment,
              actual_file: ComparisonActualFileResolver,
              ) -> ComparisonActualFile:
        """
        :return: The resolved path
        """
        failure_message = actual_file.file_check_failure(environment)
        if failure_message:
            raise PfhFailException(failure_message)

        actual_path_value = actual_file.file_ref_resolver().resolve(environment.symbols)
        return ComparisonActualFile(actual_path_value.value_of_any_dependency(environment.home_and_sds),
                                    actual_path_value,
                                    actual_file.property_descriptor_constructor)


class IsExistingRegularFileAssertionPart(AssertionPart[ComparisonActualFile, ComparisonActualFile]):
    """
    :raises PfhHardErrorException: The file is not an existing regular file (symlinks followed).
    """

    def __init__(self):
        super().__init__()
        self._file_prop_check = FileSystemElementPropertiesMatcher(
            file_properties.ActualFilePropertiesResolver(file_properties.FileType.REGULAR,
                                                         follow_symlinks=True))

    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              custom_environment,
              actual_file: ComparisonActualFile,
              ) -> ComparisonActualFile:
        element_ref = FileSystemElementReference(file_ref_resolvers.constant(actual_file.actual_file),
                                                 actual_file.actual_file_path)
        err_msg_resolver = self._file_prop_check.matches(element_ref)

        if err_msg_resolver:
            err_msg_env = err_msg_env_from_instr_env(environment)
            err_msg = err_msg_resolver.resolve(err_msg_env)
            raise PfhHardErrorException(err_msg)

        return actual_file
