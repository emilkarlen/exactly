from exactly_lib.instructions.assert_.utils.assertion_part import AssertionPart
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.type_system.logic.string_matcher import FileToCheck


class FileContentsAssertionPart(AssertionPart[FileToCheck, FileToCheck]):
    """
    A :class:`AssertionPart` that is given
    the path of a file to operate on.

    This class is just a marker for more informative types.

    Behaviour is identical to :class:`AssertionPart`.
    """

    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              custom_environment,
              file_to_check: FileToCheck
              ) -> FileToCheck:
        raise NotImplementedError('abstract method')
