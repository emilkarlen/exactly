import pathlib

from exactly_lib.instructions.assert_.utils.file_contents.actual_files import ComparisonActualFile
from exactly_lib.instructions.assert_.utils.return_pfh_via_exceptions import PfhFailException
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.result import pfh


class ContentsChecker:
    """Checks the contents of an existing file."""

    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              actual_file: ComparisonActualFile) -> pfh.PassOrFailOrHardError:
        raise NotImplementedError('todo')


class ExistenceChecker:
    """
    Checks existence of a :class:`ComparisonActualFile`,

    and returns it's path, if it exists.

    :raises PfhFailException: File does not exist.
    """

    def __init__(self, file: ComparisonActualFile):
        self._file = file

    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices
              ) -> pathlib.Path:
        failure_message = self._file.file_check_failure(environment)
        if failure_message:
            raise PfhFailException(failure_message)

        return self._file.file_path(environment)
