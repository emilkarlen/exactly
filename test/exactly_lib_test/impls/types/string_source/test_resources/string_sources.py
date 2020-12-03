from contextlib import contextmanager
from typing import Sequence, ContextManager, Iterator

from exactly_lib.impls.types.string_source import source_from_lines
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace
from exactly_lib_test.type_val_prims.string_source.test_resources.string_source_base import StringSourceTestImplBase


class SourceFromLinesTestImpl(source_from_lines.StringSourceFromLinesBase, StringSourceTestImplBase):
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
    def may_depend_on_external_resources(self) -> bool:
        return False

    @property
    @contextmanager
    def as_lines(self) -> ContextManager[Iterator[str]]:
        yield iter(self.lines)
