from typing import Sequence

from exactly_lib.instructions.assert_.utils.assertion_part import AssertionPart, IdentityAssertionPart
from exactly_lib.instructions.assert_.utils.file_contents.actual_files import ComparisonActualFileConstructor, \
    ComparisonActualFile
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, InstructionSourceInfo
from exactly_lib.test_case_utils import file_properties, path_check
from exactly_lib.test_case_utils import pfh_exception
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
        self._is_regular_file_check = file_properties.must_exist_as(file_properties.FileType.REGULAR,
                                                                    follow_symlinks=True)

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
            mb_failure = path_check.failure_message_or_none(self._is_regular_file_check, actual_file.path)

            if mb_failure:
                raise pfh_exception.PfhHardErrorException(mb_failure)
