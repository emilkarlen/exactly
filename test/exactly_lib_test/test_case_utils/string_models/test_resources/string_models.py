from contextlib import contextmanager
from typing import Sequence, ContextManager, Iterator

from exactly_lib.test_case_utils.string_models import model_from_lines
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace


class ModelFromLinesTestImpl(model_from_lines.StringModelFromLinesBase):
    def __init__(self,
                 raw_lines: Sequence[str],
                 tmp_file_space: DirFileSpace,
                 ):
        """
        :param raw_lines: Alla lines but last must end with new-line.  Last line may be ended by new-line.
        """
        super().__init__()
        self.lines = raw_lines
        self.tmp_file_space = tmp_file_space

    @property
    def _tmp_file_space(self) -> DirFileSpace:
        return self.tmp_file_space

    @property
    @contextmanager
    def as_lines(self) -> ContextManager[Iterator[str]]:
        yield iter(self.lines)
