import pathlib
from contextlib import contextmanager

from exactly_lib.instructions.assert_.utils.assertion_part import AssertionPart
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case_utils.file_transformer.file_transformer import DestinationFilePathGetter
from exactly_lib.type_system.logic.lines_transformer import LinesTransformer
from exactly_lib.util.file_utils import ensure_parent_directory_does_exist


class FileToCheck:
    """
    Access to the file to check, with functionality designed to
    help assertions on the contents of the file.
    """

    def __init__(self,
                 original_file_path: pathlib.Path,
                 environment: InstructionEnvironmentForPostSdsStep,
                 lines_transformer: LinesTransformer,
                 destination_file_path_getter: DestinationFilePathGetter):
        self._environment = environment
        self._original_file_path = original_file_path
        self._transformed_file_path = None
        self._lines_transformer = lines_transformer
        self._destination_file_path_getter = destination_file_path_getter

    @property
    def original_file_path(self) -> pathlib.Path:
        return self._original_file_path

    def transformed_file_path(self) -> pathlib.Path:
        """
        Gives a path to a file with contents that has been transformed using the transformer.
        """
        if self._transformed_file_path is not None:
            return self._transformed_file_path
        self._transformed_file_path = self._destination_file_path_getter.get(self._environment,
                                                                             self._original_file_path)
        ensure_parent_directory_does_exist(self._transformed_file_path)
        self._write_transformed_contents()
        return self._transformed_file_path

    @property
    def lines_transformer(self) -> LinesTransformer:
        return self._lines_transformer

    @contextmanager
    def lines(self) -> iter:
        """
        Gives the lines of the file contents to check.

        Lines are generated each time this method is called,
        so if it is needed to iterate over them multiple times,
        it might be better to store the result in a file,
        using transformed_file_path.
        """
        with self._original_file_path.open() as f:
            yield self._lines_transformer.transform(self._environment.home_and_sds, f)

    def _write_transformed_contents(self):
        with self._transformed_file_path.open('w') as dst_file:
            with self.lines() as lines:
                for line in lines:
                    dst_file.write(line)


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
              ) -> FileToCheck:
        raise NotImplementedError('abstract method')
