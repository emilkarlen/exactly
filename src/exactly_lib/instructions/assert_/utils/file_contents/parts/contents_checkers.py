from typing import Sequence

from exactly_lib.common.report_rendering import text_docs
from exactly_lib.instructions.assert_.utils.assertion_part import AssertionPart
from exactly_lib.instructions.assert_.utils.file_contents.actual_files import ComparisonActualFileResolver, \
    ComparisonActualFileConstructor
from exactly_lib.instructions.utils.error_messages import err_msg_env_from_instr_env
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, InstructionSourceInfo
from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils import pfh_exception
from exactly_lib.test_case_utils.err_msg2.described_path import DescribedPathPrimitive
from exactly_lib.test_case_utils.err_msg2.path_impl import described_path_resolvers
from exactly_lib.test_case_utils.file_system_element_matcher import \
    FileSystemElementPropertiesMatcher
from exactly_lib.type_system.error_message import FilePropertyDescriptorConstructor
from exactly_lib.type_system.logic.string_matcher import DestinationFilePathGetter, FileToCheck
from exactly_lib.type_system.logic.string_transformer import IdentityStringTransformer


class ComparisonActualFile(tuple):
    def __new__(cls,
                actual_path: DescribedPathPrimitive,
                checked_file_describer: FilePropertyDescriptorConstructor,
                ):
        return tuple.__new__(cls, (checked_file_describer, actual_path))

    @property
    def checked_file_describer(self) -> FilePropertyDescriptorConstructor:
        return self[0]

    @property
    def path(self) -> DescribedPathPrimitive:
        return self[1]


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
        actual_file_path = file_to_transform.path.primitive

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
            raise pfh_exception.PfhFailException(failure_message)

        actual_path = described_path_resolvers.of(actual_file.file_ref_resolver()) \
            .resolve(environment.symbols) \
            .value_of_any_dependency(environment.home_and_sds)
        return ComparisonActualFile(actual_path,
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
        err_msg_resolver = self._file_prop_check.matches(actual_file.path)

        if err_msg_resolver:
            err_msg_env = err_msg_env_from_instr_env(environment)
            err_msg = err_msg_resolver.resolve(err_msg_env)
            raise pfh_exception.PfhHardErrorException((text_docs.single_pre_formatted_line_object(err_msg)))

        return actual_file
