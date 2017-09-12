import pathlib

from exactly_lib.instructions.assert_.utils.assertion_part import AssertionPart
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep


class FileToCheck:
    """
    Access to the file to check, with functionality designed to
    help assertions on the contents of the file.
    """

    def __init__(self, path: pathlib.Path):
        self._path = path

    @property
    def path(self) -> pathlib.Path:
        return self._path


class ActualFileAssertionPart(AssertionPart):
    """
    A :class:`AssertionPart` that is given
    the path of a file to operate on.

    This class is just a marker for more informative types.

    Behaviour is identical to :class:`AssertionPart`.
    """

    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              file_to_check: FileToCheck
              ):
        return super().check(environment, os_services, file_to_check)
