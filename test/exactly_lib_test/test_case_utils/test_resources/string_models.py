from contextlib import contextmanager
from typing import ContextManager, Iterator, Sequence, List

from exactly_lib.test_case_utils.string_models.model_from_lines import StringModelFromLinesBase
from exactly_lib.type_system.logic.string_model import StringModel
from exactly_lib.util.file_utils.tmp_file_space import TmpDirFileSpace
from exactly_lib.util.file_utils.tmp_file_spaces import TmpDirFileSpaceThatMustNoBeUsed


class StringModelFromLines(StringModelFromLinesBase):
    def __init__(self,
                 value: Sequence[str],
                 tmp_file_space: TmpDirFileSpace,
                 ):
        super().__init__()
        self._value = value
        self.__tmp_file_space = tmp_file_space

    @property
    def _tmp_file_space(self) -> TmpDirFileSpace:
        return self.__tmp_file_space

    @property
    @contextmanager
    def as_lines(self) -> ContextManager[Iterator[str]]:
        yield iter(self._value)


def of_lines(
        lines: Sequence[str],
        tmp_file_space: TmpDirFileSpace = TmpDirFileSpaceThatMustNoBeUsed(),
) -> StringModel:
    return StringModelFromLines(
        lines,
        tmp_file_space,
    )


def of_string(
        contents: str,
        tmp_file_space: TmpDirFileSpace = TmpDirFileSpaceThatMustNoBeUsed(),
) -> StringModel:
    return StringModelFromLines(
        contents.splitlines(keepends=True),
        tmp_file_space,
    )


def as_lines_list(model: StringModel) -> List[str]:
    with model.as_lines as lines:
        return list(lines)


def as_string(model: StringModel) -> str:
    with model.as_lines as lines:
        return ''.join(lines)
