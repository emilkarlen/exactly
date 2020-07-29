from contextlib import contextmanager
from pathlib import Path
from typing import ContextManager, Iterator, Sequence, List

from exactly_lib.test_case.hard_error import HardErrorException
from exactly_lib.test_case_utils.string_models.model_from_lines import StringModelFromLinesBase
from exactly_lib.type_system.logic.string_model import StringModel
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace
from exactly_lib.util.file_utils.dir_file_spaces import DirFileSpaceThatMustNoBeUsed
from exactly_lib_test.common.test_resources import text_doc_assertions


class StringModelThatMustNotBeUsed(StringModel):
    @property
    def _tmp_file_space(self) -> DirFileSpace:
        raise ValueError('unsupported')

    @property
    def as_file(self) -> Path:
        raise ValueError('unsupported')

    @property
    def as_lines(self) -> ContextManager[Iterator[str]]:
        raise ValueError('unsupported')


class StringModelThatRaisesHardErrorException(StringModel):
    def __init__(self, err_msg='hard error message'):
        self._err_msg = err_msg

    @property
    def _tmp_file_space(self) -> DirFileSpace:
        raise ValueError('unsupported')

    @property
    def as_file(self) -> Path:
        return self._raise_hard_error()

    @property
    def as_lines(self) -> ContextManager[Iterator[str]]:
        return self._raise_hard_error()

    def _raise_hard_error(self):
        raise HardErrorException(
            text_doc_assertions.new_single_string_text_for_test(self._err_msg)
        )


class StringModelFromLines(StringModelFromLinesBase):
    def __init__(self,
                 value: Sequence[str],
                 tmp_file_space: DirFileSpace,
                 ):
        super().__init__()
        self._value = value
        self.__tmp_file_space = tmp_file_space

    @property
    def _tmp_file_space(self) -> DirFileSpace:
        return self.__tmp_file_space

    @property
    @contextmanager
    def as_lines(self) -> ContextManager[Iterator[str]]:
        yield iter(self._value)


def of_lines(
        lines: Sequence[str],
        tmp_file_space: DirFileSpace = DirFileSpaceThatMustNoBeUsed(),
) -> StringModel:
    return StringModelFromLines(
        lines,
        tmp_file_space,
    )


def of_string(
        contents: str,
        tmp_file_space: DirFileSpace = DirFileSpaceThatMustNoBeUsed(),
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
