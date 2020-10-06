import unittest
from contextlib import contextmanager
from pathlib import Path
from typing import ContextManager, Iterator, Sequence, List, IO

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

    def write_to(self, output: IO):
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

    def write_to(self, output: IO):
        self._raise_hard_error()

    def _raise_hard_error(self):
        raise HardErrorException(
            text_doc_assertions.new_single_string_text_for_test(self._err_msg)
        )


class StringModelThatThatChecksLines(StringModel):
    def __init__(self,
                 put: unittest.TestCase,
                 checked: StringModel,
                 ):
        self._put = put
        self._checked = checked

    @property
    def _tmp_file_space(self) -> DirFileSpace:
        return self._checked._tmp_file_space

    @property
    def as_file(self) -> Path:
        return self._checked.as_file

    @property
    @contextmanager
    def as_lines(self) -> ContextManager[Iterator[str]]:
        with self._checked.as_lines as lines:
            yield self._check_and_return_iterator(lines)

    def write_to(self, output: IO):
        self._checked.write_to(output)

    def _check_and_return_iterator(self, lines: Iterator[str]) -> Iterator[str]:
        for line in lines:
            current_line = line
            self._check_any_line(current_line)
            yield current_line
            break
        else:
            return

        for next_line in lines:
            self._check_non_last_line(current_line)
            current_line = next_line
            self._check_any_line(current_line)
            yield current_line

    def _check_any_line(self, line: str):
        if line == '':
            return
        match_idx = line.find('\n\n')
        if match_idx != -1:
            self._put.fail('Multiple new-lines: ' + repr(line))
        match_idx = line.find('\n')
        if match_idx != -1:
            if match_idx != len(line) - 1:
                self._put.fail('New-line is not final char: ' + repr(line))

    def _check_non_last_line(self, line: str):
        if line == '':
            self._put.fail('Non-last line: is empty')
        last_char = line[-1]
        if last_char != '\n':
            self._put.fail('Non-last line: last char is not new-line: ' + repr(line))


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
