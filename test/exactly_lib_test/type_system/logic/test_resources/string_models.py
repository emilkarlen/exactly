from pathlib import Path
from typing import ContextManager, Iterator

from exactly_lib.type_system.logic.hard_error import HardErrorException
from exactly_lib.type_system.logic.string_model import StringModel
from exactly_lib.util.file_utils.tmp_file_space import TmpDirFileSpace
from exactly_lib_test.common.test_resources import text_doc_assertions


class StringModelThatMustNotBeUsed(StringModel):
    @property
    def _tmp_file_space(self) -> TmpDirFileSpace:
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
    def _tmp_file_space(self) -> TmpDirFileSpace:
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
