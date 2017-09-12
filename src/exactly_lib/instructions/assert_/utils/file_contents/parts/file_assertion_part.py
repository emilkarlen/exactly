import pathlib
from contextlib import contextmanager

from exactly_lib.instructions.assert_.utils.assertion_part import AssertionPart
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.type_system.logic.lines_transformer import LinesTransformer


class FileToCheck:
    """
    Access to the file to check, with functionality designed to
    help assertions on the contents of the file.
    """

    def __init__(self,
                 original_file_path: pathlib.Path,
                 transformed_file_path: pathlib.Path,
                 lines_transformer: LinesTransformer):
        self._original_file_path = original_file_path
        self._transformed_file_path = transformed_file_path
        self._lines_transformer = lines_transformer

    @property
    def original_file_path(self) -> pathlib.Path:
        return self._original_file_path

    @property
    def transformed_file_path(self) -> pathlib.Path:
        return self._transformed_file_path

    @property
    def lines_transformer(self) -> LinesTransformer:
        return self._lines_transformer

    @contextmanager
    def lines(self, tcds: HomeAndSds) -> iter:
        """
        Gives the lines of the file contents to check
        """
        with self._transformed_file_path.open() as f:
            yield self._lines_transformer.transform(tcds, f)


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
        raise NotImplementedError('abstract method')
