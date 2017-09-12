import pathlib

from exactly_lib.instructions.assert_.utils.assertion_part import AssertionPart
from exactly_lib.instructions.assert_.utils.file_contents.actual_files import ComparisonActualFile
from exactly_lib.instructions.assert_.utils.file_contents.parts.file_assertion_part import FileToCheck
from exactly_lib.instructions.assert_.utils.return_pfh_via_exceptions import PfhFailException, PfhHardErrorException
from exactly_lib.named_element.resolver_structure import LinesTransformerResolver
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case_utils.file_transformer.file_transformer import DestinationFilePathGetter


class FileExistenceAssertionPart(AssertionPart):
    """
    Checks existence of a :class:`ComparisonActualFile`,

    and returns it's path, if it exists.

    :raises PfhFailException: File does not exist.
    """

    def __init__(self, actual_file: ComparisonActualFile):
        super().__init__()
        self._actual_file = actual_file

    @property
    def references(self) -> list:
        return self._actual_file.references

    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              not_used,
              ) -> pathlib.Path:
        """
        :return: The resolved path
        """
        failure_message = self._actual_file.file_check_failure(environment)
        if failure_message:
            raise PfhFailException(failure_message)

        return self._actual_file.file_path(environment)


class FileTransformerAsAssertionPart(AssertionPart):
    """
    Transforms a given existing file.

    Does not check any property.

    :raises PfhPfhHardErrorException: The transformation fails
    """

    def __init__(self, lines_transformer_resolver: LinesTransformerResolver):
        super().__init__()
        self._lines_transformer_resolver = lines_transformer_resolver

    @property
    def references(self) -> list:
        return self._lines_transformer_resolver.references

    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              file_to_transform: pathlib.Path,
              ) -> FileToCheck:
        """
        :param file_to_transform: The file that should be transformed
        :return: The path of the transformed file.
        """
        if not file_to_transform.is_file():
            raise PfhHardErrorException('Not an existing regular file: ' + str(file_to_transform))

        lines_transformer = self._lines_transformer_resolver.resolve(environment.symbols)
        return FileToCheck(file_to_transform,
                           environment,
                           lines_transformer,
                           DestinationFilePathGetter())
