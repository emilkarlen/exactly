import pathlib
import tempfile
from contextlib import contextmanager

from exactly_lib.instructions.assert_.utils.file_contents.parts.file_assertion_part import DestinationFilePathGetter
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep


@contextmanager
def destination_file_path_getter_that_gives_seq_of_unique_paths() -> DestinationFilePathGetter:
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield _DestinationFilePathGetter(pathlib.Path(tmp_dir))


class _DestinationFilePathGetter(DestinationFilePathGetter):
    def __init__(self, tmp_dir: pathlib.Path):
        super().__init__()
        self.tmp_dir = tmp_dir
        self._file_num = 0

    def get(self,
            environment: InstructionEnvironmentForPostSdsStep,
            src_file_path: pathlib.Path) -> pathlib.Path:
        self._file_num += 1
        return self.tmp_dir / (str(self._file_num) + '.txt')
