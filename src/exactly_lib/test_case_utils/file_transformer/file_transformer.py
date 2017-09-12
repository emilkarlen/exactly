import pathlib

from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.type_system.logic.lines_transformer import LinesTransformer


class DestinationFilePathGetter:
    """
    Gets a file name that can be used for storing intermediate file contents.
    """

    def get(self,
            environment: InstructionEnvironmentForPostSdsStep,
            src_file_path: pathlib.Path) -> pathlib.Path:
        """
        :return: Path of a non-existing file.
        """
        instruction_dir = environment.phase_logging.unique_instruction_file_as_existing_dir()
        dst_file_base_name = src_file_path.name
        return instruction_dir / dst_file_base_name


class FileTransformer:
    """ Transforms an existing regular file. """

    # TODO: Maybe this class should be removed,
    # it is a wrapping of new LinesTransformer into old structures.
    # But perhaps it is motivated to have it. Have not looked into it.

    @property
    def destination_file_path_getter(self) -> DestinationFilePathGetter:
        return DestinationFilePathGetter()

    def transform(self,
                  environment: InstructionEnvironmentForPostSdsStep,
                  os_services: OsServices,
                  src_file_path: pathlib.Path) -> pathlib.Path:
        raise NotImplementedError('abstract method')

    @property
    def corresponding_lines_transformer(self) -> LinesTransformer:
        raise NotImplementedError('abstract method')
