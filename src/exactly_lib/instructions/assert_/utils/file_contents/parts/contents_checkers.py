from typing import Sequence

from exactly_lib.instructions.assert_.utils.assertion_part import AssertionPart, IdentityAssertionPart
from exactly_lib.instructions.assert_.utils.file_contents.actual_files import ComparisonActualFileConstructor, \
    ComparisonActualFile
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, InstructionSourceInfo
from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils import pfh_exception
from exactly_lib.test_case_utils.file_system_element_matcher import \
    FileSystemElementPropertiesMatcher
from exactly_lib.test_case_utils.string_transformer.impl.identity import IdentityStringTransformer
from exactly_lib.type_system.logic.string_matcher import DestinationFilePathGetter, FileToCheck


class FileConstructorAssertionPart(AssertionPart[ComparisonActualFileConstructor, ComparisonActualFile]):
    """
    Constructs the actual file.
    """

    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              custom_environment: InstructionSourceInfo,
              value_to_check: ComparisonActualFileConstructor) -> ComparisonActualFile:
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
        return FileToCheck(file_to_transform.path,
                           IdentityStringTransformer(),
                           DestinationFilePathGetter())


class IsExistingRegularFileAssertionPart(IdentityAssertionPart[ComparisonActualFile]):
    """
    :raises pfh_exception.PfhFailException: The file is not an existing regular file (symlinks followed).
    """

    def __init__(self):
        super().__init__()
        self._file_prop_check = FileSystemElementPropertiesMatcher(
            file_properties.ActualFilePropertiesResolver(file_properties.FileType.REGULAR,
                                                         follow_symlinks=True))

    def _check(self,
               environment: InstructionEnvironmentForPostSdsStep,
               os_services: OsServices,
               custom_environment,
               actual_file: ComparisonActualFile,
               ):
        if actual_file.file_access_needs_to_be_verified:
            self.__check(actual_file)

    def __check(self, actual_file: ComparisonActualFile,
                ):
        if actual_file.file_access_needs_to_be_verified:
            err_msg_resolver = self._file_prop_check.matches(actual_file.path)

            if err_msg_resolver:
                raise pfh_exception.PfhFailException(err_msg_resolver.resolve__tr())
