from contextlib import contextmanager
from typing import Sequence, ContextManager, Iterator, Optional, TextIO

from exactly_lib.definitions.primitives import string_source as _primitive_defs
from exactly_lib.impls.types.string_source import cached_frozen
from exactly_lib.impls.types.string_source.contents.contents_with_cached_path import \
    ContentsWithCachedPathFromWriteToBase
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.type_val_prims.string_source.structure_builder import StringSourceStructureBuilder
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace


def string_source_of_mb_empty_sequence(parts: Sequence[StringSource],
                                       mem_buff_size: int,
                                       file_name: str = 'concat') -> Optional[StringSource]:
    if not parts:
        return None
    elif len(parts) == 1:
        return parts[0]
    else:
        return string_source(parts, mem_buff_size, file_name)


def string_source_of_non_empty_sequence(parts: Sequence[StringSource],
                                        mem_buff_size: int,
                                        file_name: str = 'concat') -> StringSource:
    if len(parts) == 1:
        return parts[0]
    else:
        return string_source(parts, mem_buff_size, file_name)


def string_source(parts: Sequence[StringSource],
                  mem_buff_size: int,
                  file_name: str = 'concat'
                  ) -> StringSource:
    """
    :param parts: Must contain at least 2 elements
    """

    def new_structure_builder() -> StringSourceStructureBuilder:
        return StringSourceStructureBuilder(
            _primitive_defs.CONCAT_NAME,
            (),
            [part.structure() for part in parts]
        )

    return cached_frozen.StringSourceWithCachedFrozen(
        new_structure_builder,
        _ConcatStringSourceContents(parts, file_name),
        mem_buff_size,
        file_name,
    )


class _ConcatStringSourceContents(ContentsWithCachedPathFromWriteToBase):
    def __init__(self,
                 parts: Sequence[StringSource],
                 file_name: str,
                 ):
        super().__init__(file_name)
        self._parts = parts

    @property
    def may_depend_on_external_resources(self) -> bool:
        return any([
            part.contents().may_depend_on_external_resources
            for part in self._parts
        ])

    @property
    @contextmanager
    def as_lines(self) -> ContextManager[Iterator[str]]:
        yield self._lines_iter()

    @property
    def as_str(self) -> str:
        return ''.join(self._lines_iter())

    def write_to(self, output: TextIO):
        for part in self._parts:
            part.contents().write_to(output)

    @property
    def tmp_file_space(self) -> DirFileSpace:
        return self._parts[0].contents().tmp_file_space

    def _lines_iter(self) -> Iterator[str]:
        last_line_wo_ending_new_line = None

        def append_to_last_line_wo_ending_new_line(s: str) -> str:
            return (
                s
                if last_line_wo_ending_new_line is None
                else
                last_line_wo_ending_new_line + s
            )

        for non_last_part in self._parts[:-1]:
            with non_last_part.contents().as_lines as non_last_part_lines:
                for first_line in non_last_part_lines:
                    if _is_ended_by_new_line(first_line):
                        yield append_to_last_line_wo_ending_new_line(first_line)
                        last_line_wo_ending_new_line = None
                    else:
                        last_line_wo_ending_new_line = append_to_last_line_wo_ending_new_line(first_line)
                    break
                for non_first_line in non_last_part_lines:
                    if _is_ended_by_new_line(non_first_line):
                        yield non_first_line
                    else:
                        last_line_wo_ending_new_line = non_first_line

        with self._parts[-1].contents().as_lines as last_part_lines:
            for first_line in last_part_lines:
                yield append_to_last_line_wo_ending_new_line(first_line)
                break
            else:
                # last part is empty
                if last_line_wo_ending_new_line is not None:
                    yield last_line_wo_ending_new_line
            for non_first_line in last_part_lines:
                yield non_first_line


def _is_ended_by_new_line(s: str) -> bool:
    return s != '' and s[-1] == '\n'
