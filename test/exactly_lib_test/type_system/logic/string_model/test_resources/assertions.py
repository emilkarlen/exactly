import unittest
from contextlib import contextmanager
from pathlib import Path
from typing import ContextManager, Iterator, IO

from exactly_lib.type_system.logic.string_model import StringModel
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertionBase, MessageBuilder


class StringModelLinesAreValidAssertion(ValueAssertionBase[StringModel]):
    def _apply(self,
               put: unittest.TestCase,
               value: StringModel,
               message_builder: MessageBuilder,
               ):
        model_checker = StringModelThatThatChecksLines(put, value)
        self._check_lines_by_iterating_over_them(model_checker)

    @staticmethod
    def _check_lines_by_iterating_over_them(model_checker: StringModel):
        with model_checker.as_lines as lines:
            for _ in lines:
                pass


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
