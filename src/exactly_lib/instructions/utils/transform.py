import pathlib

from exactly_lib.instructions.multi_phase_instructions.utils import file_creation
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.type_system.logic.lines_transformer import LinesTransformer


def create_file_from_transformation_of_existing_file(src_path: pathlib.Path,
                                                     dst_path: pathlib.Path,
                                                     transformer: LinesTransformer,
                                                     tcds: HomeAndSds) -> str:
    """
    :return: Error message in case of failure
    """

    def write_file(output_file):
        with src_path.open() as in_file:
            for line in transformer.transform(tcds, in_file):
                output_file.write(line)

    return file_creation.create_file(dst_path,
                                     write_file)
