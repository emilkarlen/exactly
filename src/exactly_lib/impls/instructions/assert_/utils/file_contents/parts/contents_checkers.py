from typing import Sequence

from exactly_lib.impls import file_properties
from exactly_lib.impls.exception import pfh_exception
from exactly_lib.impls.instructions.assert_.utils.assertion_part import AssertionPart, IdentityAssertionPart
from exactly_lib.impls.instructions.assert_.utils.file_contents.actual_files import ComparisonActualFileConstructor, \
    ComparisonActualFile
from exactly_lib.impls.types.path import path_check
from exactly_lib.impls.types.string_source import file_source
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep
from exactly_lib.type_val_prims.string_source.string_source import StringSource


class FileConstructorAssertionPart(AssertionPart[ComparisonActualFileConstructor, ComparisonActualFile]):
    """
    Constructs the actual file.
    """

    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              value_to_check: ComparisonActualFileConstructor) -> ComparisonActualFile:
        return value_to_check.construct(environment,
                                        os_services)


class ConstructFileToCheckAssertionPart(AssertionPart[ComparisonActualFile, StringSource]):
    @property
    def references(self) -> Sequence[SymbolReference]:
        return ()

    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              file_to_transform: ComparisonActualFile,
              ) -> StringSource:
        return file_source.string_source_of_file__described(
            file_to_transform.path,
            environment.tmp_dir__path_access.paths_access,
        )


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
